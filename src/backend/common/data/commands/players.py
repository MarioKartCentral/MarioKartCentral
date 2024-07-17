from dataclasses import dataclass
from typing import Callable, List, Literal
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
                match = re.fullmatch(r"\d{4}-\d{4}-\d{4}", friend_code.fc)
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
class ListPlayersCommand(Command[PlayerList]):
    filter: PlayerFilter

    async def handle(self, db_wrapper, s3_wrapper):
        filter = self.filter
        async with db_wrapper.connect(readonly=True) as db:

            where_clauses: list[str] = []
            fc_where_clauses: list[str] = []

            variable_parameters: list[Any] = []
            
            limit:int = 50
            offset:int = 0

            if filter.page is not None:
                offset = (filter.page - 1) * limit

            def append_equal_filter(filter_value: Any, column_name: str):
                if filter_value is not None:
                    where_clauses.append(f"{column_name} = ?")
                    variable_parameters.append(filter_value)

            if filter.name is not None:
                where_clauses.append(f"name LIKE ?")
                variable_parameters.append(f"%{filter.name}%")

            append_equal_filter(filter.country, "country_code")
            append_equal_filter(filter.is_hidden, "is_hidden")
            append_equal_filter(filter.is_shadow, "is_shadow")
            append_equal_filter(filter.is_banned, "is_banned")
            append_equal_filter(filter.discord_id, "discord_id")

            # make sure that player is in a team roster which is linked to the passed-in squad ID
            if filter.squad_id is not None:
                where_clauses.append(f"""p.id IN (
                                     SELECT m.player_id FROM team_members m
                                     JOIN team_squad_registrations r ON r.roster_id = m.roster_id
                                     WHERE r.squad_id IS ? AND m.leave_date IS ?
                )""")
                variable_parameters.append(filter.squad_id)
                variable_parameters.append(None)

            if filter.friend_code or filter.name_or_fc or filter.game:

                if filter.friend_code is not None:
                    fc_where_clauses.append("fc LIKE ?")
                    variable_parameters.append(f"%{filter.friend_code}%")

                # check names and friend codes
                if filter.name_or_fc:
                    fc_where_clauses.append("(fc LIKE ? OR p.name LIKE ?)")
                    variable_parameters.append(f"%{filter.name_or_fc}%")
                    variable_parameters.append(f"%{filter.name_or_fc}%")

                if filter.game is not None:
                    fc_where_clauses.append("game = ?")
                    variable_parameters.append(filter.game)

                fc_where_clauses_str = ' AND '.join(fc_where_clauses)
                #fc_where_clauses.extend(where_clauses)
                where_clauses.append(f"id IN (SELECT player_id FROM friend_codes WHERE {fc_where_clauses_str})")

            player_where_clause = "" if not where_clauses else f" WHERE {' AND '.join(where_clauses)}"
            players_query = f"SELECT p.id, name, country_code, is_hidden, is_shadow, is_banned, discord_id FROM players p {player_where_clause} ORDER BY name LIMIT ? OFFSET ? "

            fc_where_clause = ""
            fc_where_clauses = []
            fc_variable_parameters: list[Any] = []
            # for player search, we want to return only the FCs with matching game and/or fc that we typed in
            if filter.detailed and filter.matching_fcs_only:
                if filter.game is not None:
                    fc_where_clauses.append("game = ?")
                    fc_variable_parameters.append(filter.game)
                if filter.friend_code:
                    fc_where_clauses.append("fc LIKE ?")
                    fc_variable_parameters.append(f"%{filter.friend_code}%")
                if filter.name_or_fc:
                    match = re.fullmatch(r"\d{4}-\d{4}-\d{4}", filter.name_or_fc)
                    if match:
                        fc_where_clauses.append("fc LIKE ?")
                        fc_variable_parameters.append(f"%{filter.name_or_fc}%")
                fc_where_clause = "" if not len(fc_where_clauses) else f"AND {' AND '.join(fc_where_clauses)}"
            friend_codes_query = f"""SELECT id, fc, game, player_id, is_verified, is_primary, description FROM friend_codes f WHERE player_id IN (
                SELECT p.id FROM players p {player_where_clause} {fc_where_clause} LIMIT ? OFFSET ?
            )"""

            count_query = f"SELECT COUNT (*) FROM (SELECT p.id FROM players p {player_where_clause})"

            players: List[PlayerAndFriendCodes] = []
            friend_codes: dict[int, list[FriendCode]] = {}

            print(players_query)
            async with db.execute(players_query, (*variable_parameters, limit, offset)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    id, name, country_code, is_hidden, is_shadow, is_banned, discord_id = row
                    player = PlayerAndFriendCodes(id, name, country_code, is_hidden, is_shadow, is_banned, discord_id, [])
                    players.append(player)
                    friend_codes[player.id] = player.friend_codes

            page_count: int = 0
            player_count: int = 0
            async with db.execute(count_query, variable_parameters) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                player_count = row[0]

            page_count = int(player_count / limit) + (1 if player_count % limit else 0)

            if filter.detailed is not None:
                async with db.execute(friend_codes_query, (*(variable_parameters + fc_variable_parameters), limit, offset)) as cursor:
                    rows = await cursor.fetchall()
                    for row in rows:
                        id, fc, game, player_id, is_verified, is_primary, description = row
                        friend_codes[player_id].append(FriendCode(id, fc, game, player_id, is_verified, is_primary, description))
                
            return PlayerList(players, player_count, page_count)
