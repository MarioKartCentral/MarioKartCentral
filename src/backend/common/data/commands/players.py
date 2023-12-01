from dataclasses import dataclass
from typing import Callable, Literal
import re

from aiosqlite import Connection

from common.data.commands import Command, save_to_command_log
from common.data.models import *


@save_to_command_log
@dataclass
class CreatePlayerCommand(Command[Player]):
    user_id: int | None
    data: CreatePlayerRequestData

    async def handle(self, db_wrapper, s3_wrapper):
        data = self.data
        async with db_wrapper.connect() as db:
            if self.user_id is not None:
                async with db.execute("SELECT player_id FROM users WHERE id = ?", (self.user_id,)) as cursor:
                    row = await cursor.fetchone()
                    assert row is not None
                    if row[0] is not None:
                        raise Problem("Can only have one player per user", status=400)
            command = """INSERT INTO players(name, country_code, is_hidden, is_shadow, is_banned, discord_id) 
                VALUES (?, ?, ?, ?, ?, ?)"""
            player_row = await db.execute_insert(
                command, 
                (data.name, data.country_code, data.is_hidden, data.is_shadow, False, data.discord_id))
            
            # TODO: Run queries to determine why it errored
            if player_row is None:
                raise Problem("Failed to create player")
            
            player_id = player_row[0]

            if self.user_id is not None:
                async with db.execute("UPDATE users SET player_id = ? WHERE id = ?", (player_id, self.user_id)) as cursor:
                    # handle case where user with the given ID doesn't exist
                    if cursor.rowcount != 1:
                        raise Problem("Invalid User ID", status=404)
                    
            fc_set = set([friend_code.fc for friend_code in data.friend_codes])
            if len(fc_set) < len(data.friend_codes):
                raise Problem("Cannot have duplicate FCs", status=400)
            fc_limits = {"mk8dx": 1, "mkt": 1, "mkw": 4, "mk7": 1, "mk8": 1}
            for game in fc_limits.keys():
                game_fcs = [fc for fc in data.friend_codes if fc.game == game]
                if len(game_fcs) > fc_limits[game]:
                    raise Problem(f"Too many friend codes were provided for the game {game} (limit {fc_limits[game]})", status=400)
                    
            for friend_code in data.friend_codes:
                match = re.match(r"\d{4}-\d{4}-\d{4}", friend_code.fc)
                if friend_code.game != "mk8" and not match:
                    raise Problem(f"FC {friend_code.fc} for game {friend_code.game} is in incorrect format", status=400)
                
                # check if friend code is currently in use
                async with db.execute("SELECT id FROM friend_codes WHERE fc = ? AND game = ? AND is_active = ?", (friend_code.fc, friend_code.game, True)) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        raise Problem("Another player is currently using this friend code for this game", status=400)
                    
            friend_code_tuples = [(player_id, friend_code.game, friend_code.fc, False, friend_code.is_primary, True, friend_code.description) for friend_code in data.friend_codes]
            await db.executemany("INSERT INTO friend_codes(player_id, game, fc, is_verified, is_primary, is_active, description) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    friend_code_tuples)
            await db.commit()
            return Player(int(player_id), data.name, data.country_code, data.is_hidden, data.is_shadow, False, data.discord_id)

@save_to_command_log
@dataclass
class UpdatePlayerCommand(Command[bool]):
    data: EditPlayerRequestData

    async def handle(self, db_wrapper, s3_wrapper) -> bool:
        data = self.data
        async with db_wrapper.connect() as db:
            update_query = """UPDATE players 
            SET name = ?, country_code = ?, is_hidden = ?, is_shadow = ?, discord_id = ?
            WHERE id = ?"""
            params = (data.name, data.country_code, data.is_hidden, data.is_shadow, data.discord_id, data.player_id)

            async with db.execute(update_query, params) as cursor:
                if cursor.rowcount != 1:
                    return False

            await db.commit()
            return True


@dataclass
class GetPlayerDetailedCommand(Command[PlayerDetailed | None]):
    id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            query = "SELECT name, country_code, is_hidden, is_shadow, is_banned, discord_id FROM players WHERE id = ?"
            async with db.execute(query, (self.id,)) as cursor:
                player_row = await cursor.fetchone()
            
            if player_row is None:
                return None
            
            name, country_code, is_hidden, is_shadow, is_banned, discord_id = player_row

            fc_query = "SELECT id, game, fc, is_verified, is_primary, description FROM friend_codes WHERE player_id = ?"
            friend_code_rows = await db.execute_fetchall(fc_query, (self.id, ))
            friend_codes = [FriendCode(id, fc, game, self.id, bool(is_verified), bool(is_primary), description) for id, game, fc, is_verified, is_primary, description in friend_code_rows]

            user_query = "SELECT id FROM users WHERE player_id = ?"
            async with db.execute(user_query, (self.id,)) as cursor:
                user_row = await cursor.fetchone()
            
            user = None if user_row is None else User(int(user_row[0]), self.id)

            rosters: list[PlayerRoster] = []
            async with db.execute("""SELECT m.roster_id, m.join_date, t.id, t.name, t.tag, t.color, r.name, r.tag, r.game, r.mode
                                    FROM team_members m
                                    JOIN team_rosters r ON m.roster_id = r.id
                                    JOIN teams t ON r.team_id = t.id
                                    WHERE m.player_id = ? AND m.leave_date IS NULL""", (self.id,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    roster_id, join_date, team_id, team_name, team_tag, color, roster_name, roster_tag, game, mode = row
                    roster_name = roster_name if roster_name else team_name
                    roster_tag = roster_tag if roster_tag else team_tag
                    rosters.append(PlayerRoster(roster_id, join_date, team_id, team_name, team_tag, color, roster_name, roster_tag, game, mode))

            ban_info = None
            if is_banned:
                ban_query = "SELECT player_id, staff_id, is_indefinite, expiration_date, reason from player_bans WHERE player_id = ?"
                async with db.execute(ban_query, (self.id,)) as cursor:
                    ban_row = await cursor.fetchone()
                ban_info = None if ban_row is None else PlayerBan(*ban_row)

            user_settings = None
            if user:
                async with db.execute("""SELECT avatar, about_me, language, 
                    color_scheme, timezone FROM user_settings WHERE user_id = ?""", (user.id,)) as cursor:
                    settings_row = await cursor.fetchone()
                    if settings_row is not None:
                        user_settings = UserSettings(user.id, *settings_row)

            return PlayerDetailed(self.id, name, country_code, is_hidden, is_shadow, is_banned, discord_id, friend_codes, rosters, ban_info, user_settings)
        
@dataclass
class ListPlayersCommand(Command[list[Player]]):
    filter: PlayerFilter

    async def handle(self, db_wrapper, s3_wrapper):
        filter = self.filter
        async with db_wrapper.connect(readonly=True) as db:
            where_clauses: list[str] = []
            variable_parameters: list[Any] = []

            def append_equal_filter(filter_value: Any, column_name: str):
                if filter_value is not None:
                    where_clauses.append(f"{column_name} = ?")
                    variable_parameters.append(filter_value)

            if filter.name is not None:
                where_clauses.append(f"name LIKE ?")
                variable_parameters.append(f"%{filter.name}%")

            append_equal_filter(filter.game, "game")
            append_equal_filter(filter.country, "country_code")
            append_equal_filter(filter.is_hidden, "is_hidden")
            append_equal_filter(filter.is_shadow, "is_shadow")
            append_equal_filter(filter.is_banned, "is_banned")
            append_equal_filter(filter.discord_id, "discord_id")

            if filter.friend_code is not None or filter.game is not None:
                fc_where_clauses: list[str] = []

                if filter.friend_code is not None:
                    fc_where_clauses.append("fc LIKE ?")
                    variable_parameters.append(f"%{filter.friend_code}%")
                
                if filter.game is not None:
                    fc_where_clauses.append("game = ?")
                    variable_parameters.append(filter.game)

                fc_where_clause = ' AND '.join(fc_where_clauses)
                where_clauses.append(f"id IN (SELECT player_id from friend_codes WHERE {fc_where_clause})")


            where_clause = "" if not where_clauses else f" WHERE {' AND '.join(where_clauses)}"
            players_query = f"SELECT id, name, country_code, is_hidden, is_shadow, is_banned, discord_id FROM players{where_clause}"

            players: list[Player] = []
            async with db.execute(players_query, variable_parameters) as cursor:
                while True:
                    batch = await cursor.fetchmany(50)
                    if not batch:
                        break

                    for row in batch:
                        id, name, country_code, is_hidden, is_shadow, is_banned, discord_id = row
                        players.append(Player(id, name, country_code, is_hidden, is_shadow, is_banned, discord_id))
            
            return players


async def player_exists_in_table(db: Connection, table: Literal['players', 'player_bans'], player_id: int) -> bool:
    """ Check if a player is in either the players or player_bans db table """
    if table == 'players':
        command = "SELECT EXISTS (SELECT 1 FROM players WHERE id = ?)"
    else:
        command = "SELECT EXISTS (SELECT 1 FROM player_bans WHERE player_id = ?)"

    async with db.execute(command, (player_id, )) as cursor:
        row = await cursor.fetchone()
        assert row is not None
        return True if row[0] else False

@save_to_command_log
@dataclass
class BanPlayerCommand(Command[PlayerBan]):
    player_id: int
    staff_id: int
    data: PlayerBanRequestData

    async def handle(self, db_wrapper, s3_wrapper):
        data = self.data

        async with db_wrapper.connect() as db:
            command = "INSERT INTO player_bans(player_id, staff_id, is_indefinite, expiration_date, reason) VALUES (?, ?, ?, ?, ?)"
            params = (self.player_id, self.staff_id, data.is_indefinite, data.expiration_date, data.reason)
            
            try:
                player_row = await db.execute_insert(command, params)
                if player_row is None:
                    raise Problem("Failed to ban player", "Failed to insert into ban table")
            except Exception as e:
                if not await player_exists_in_table(db, 'players', self.player_id):
                    raise Problem("Player not found", status=404)
                if await player_exists_in_table(db, 'player_bans', self.player_id):
                    raise Problem("Player is already banned", status=400)
                raise Problem("Error", detail=str(e))

            async with db.execute("""UPDATE players SET is_banned = TRUE WHERE id = ?""", (self.player_id,)) as cursor:
                if cursor.rowcount != 1:
                    raise Problem("Failed to ban player", "Failed to update is_banned in player table")
            
            await db.commit()
            return PlayerBan(*params)

@save_to_command_log
@dataclass
class UnbanPlayerCommand(Command[None]):
    player_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("DELETE FROM player_bans WHERE player_id = ?", (self.player_id, )) as cursor:
                rowcount = cursor.rowcount

            if rowcount != 1:
                raise Problem("Player not found", "Unable to find player in the ban table", status=404)
            
            async with db.execute("""UPDATE players SET is_banned = FALSE WHERE id = ?""", (self.player_id,)) as cursor:
                if cursor.rowcount != 1:
                    raise Problem("Failed to unban player", "Failed to update is_banned in player table")
            await db.commit()

@save_to_command_log
@dataclass
class EditPlayerBanCommand(Command[PlayerBan]):
    player_id: int
    staff_id: int
    data: PlayerBanRequestData

    async def handle(self, db_wrapper, s3_wrapper):
        data = self.data
        
        async with db_wrapper.connect() as db:
            command = "UPDATE player_bans SET staff_id = ?, is_indefinite = ?, expiration_date = ?, reason = ? WHERE player_id = ?"
            params = (self.staff_id, data.is_indefinite, data.expiration_date, data.reason, self.player_id)
            
            async with db.execute(command, params) as cursor:
                if cursor.rowcount != 1:
                    raise Problem("Player not found", "Unable to find player in the ban table", status=404)

            await db.commit()
            return PlayerBan(self.player_id, self.staff_id, data.is_indefinite, data.expiration_date, data.reason)

@dataclass
class ListBannedPlayersCommand(Command[list[PlayerBan]]):
    filter: PlayerBanFilter

    async def handle(self, db_wrapper, s3_wrapper):
        filter = self.filter

        async with db_wrapper.connect(readonly=True) as db:
            where_clauses: list[str] = []
            variable_parameters: list[Any] = []

            def append_equal_filter(filter_value: Any, clause_name: str, where_clause: str, var_param: str | None = None, cast_fn: Callable[[str], Any] | None = None):
                if filter_value is not None:
                    where_clauses.append(where_clause)
                    if var_param:
                        variable_parameters.append(var_param)
                    else:
                        if cast_fn:
                            try:
                                filter_value = cast_fn(filter_value)
                            except Exception as e:
                                raise Problem(f"Bad {clause_name} query", detail=str(e), status=400)
                        variable_parameters.append(filter_value)

            append_equal_filter(filter.player_id, 'player_id', 'player_id = ?', cast_fn=int)
            append_equal_filter(filter.staff_id, 'staff_id', 'staff_id = ?', cast_fn=int)
            append_equal_filter(filter.is_indefinite, 'is_indefinite', 'is_indefinite = ?')
            append_equal_filter(filter.expires_before, 'expires_before', 'expiration_date <= ?', cast_fn=int)
            append_equal_filter(filter.expires_after, 'expires_after', 'expiration_date >= ?', cast_fn=int)
            append_equal_filter(filter.reason, 'reason', "reason LIKE ?", var_param=f"%{filter.reason}%")

            where_clause = "" if not where_clauses else f"WHERE {' AND '.join(where_clauses)}"
            query = f"""SELECT player_id, staff_id, is_indefinite, expiration_date, reason from player_bans {where_clause}"""

            player_bans: list[PlayerBan] = []
            async with db.execute(query, variable_parameters) as cursor:
                while True:
                    batch = await cursor.fetchmany(50)
                    if not batch:
                        break

                    for row in batch:
                        player_bans.append(PlayerBan(*row))
            
            return player_bans
