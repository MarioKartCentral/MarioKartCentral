from dataclasses import dataclass
from typing import List
import re

from common.data.commands import Command, save_to_command_log
from common.data.models import *
from datetime import datetime, timedelta, timezone


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
            command = """INSERT INTO players(name, country_code, is_hidden, is_shadow, is_banned) 
                VALUES (?, ?, ?, ?, ?)"""
            player_row = await db.execute_insert(
                command, 
                (data.name, data.country_code, data.is_hidden, data.is_shadow, False))
            
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
            return Player(int(player_id), data.name, data.country_code, data.is_hidden, data.is_shadow, False, None)

@save_to_command_log
@dataclass
class UpdatePlayerCommand(Command[bool]):
    data: EditPlayerRequestData

    async def handle(self, db_wrapper, s3_wrapper) -> bool:
        data = self.data
        async with db_wrapper.connect() as db:
            update_query = """UPDATE players 
            SET name = ?, country_code = ?, is_hidden = ?, is_shadow = ?
            WHERE id = ?"""
            params = (data.name, data.country_code, data.is_hidden, data.is_shadow, data.player_id)

            async with db.execute(update_query, params) as cursor:
                if cursor.rowcount != 1:
                    return False

            await db.commit()
            return True


@dataclass
class GetPlayerDetailedCommand(Command[PlayerDetailed | None]):
    id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            query = "SELECT name, country_code, is_hidden, is_shadow, is_banned FROM players WHERE id = ?"
            async with db.execute(query, (self.id,)) as cursor:
                player_row = await cursor.fetchone()
            
            if player_row is None:
                return None
            
            name, country_code, is_hidden, is_shadow, is_banned = player_row

            fc_query = "SELECT id, game, fc, is_verified, is_primary, description, is_active FROM friend_codes WHERE player_id = ?"
            friend_code_rows = await db.execute_fetchall(fc_query, (self.id, ))
            friend_codes = [FriendCode(id, fc, game, self.id, bool(is_verified), bool(is_primary), description, bool(is_active)) for id, game, fc, is_verified, is_primary, 
                            description, is_active in friend_code_rows]

            user_query = "SELECT id FROM users WHERE player_id = ?"
            async with db.execute(user_query, (self.id,)) as cursor:
                user_row = await cursor.fetchone()
            
            user = None if user_row is None else User(int(user_row[0]), self.id)

            rosters: list[PlayerRoster] = []
            async with db.execute("""SELECT m.roster_id, m.join_date, t.id, t.name, t.tag, t.color, r.name, r.tag, r.game, r.mode, m.is_bagger_clause
                                    FROM team_members m
                                    JOIN team_rosters r ON m.roster_id = r.id
                                    JOIN teams t ON r.team_id = t.id
                                    WHERE m.player_id = ? AND m.leave_date IS NULL""", (self.id,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    roster_id, join_date, team_id, team_name, team_tag, color, roster_name, roster_tag, game, mode, is_bagger_clause = row
                    roster_name = roster_name if roster_name else team_name
                    roster_tag = roster_tag if roster_tag else team_tag
                    rosters.append(PlayerRoster(roster_id, join_date, team_id, team_name, team_tag, color, roster_name, roster_tag, game, mode, bool(is_bagger_clause)))

            ban_info = None
            if is_banned:
                ban_query = """SELECT reason FROM player_bans WHERE player_id = ?"""
                async with db.execute(ban_query, (self.id,)) as cursor:
                    ban_row = await cursor.fetchone()
                ban_info = None if ban_row is None else PlayerBanBasic(self.id, ban_row[0])

            user_settings = None
            if user:
                async with db.execute("""SELECT avatar, about_me, language, 
                    color_scheme, timezone FROM user_settings WHERE user_id = ?""", (user.id,)) as cursor:
                    settings_row = await cursor.fetchone()
                    if settings_row is not None:
                        user_settings = UserSettings(user.id, *settings_row)

            discord = None
            if user:
                async with db.execute("SELECT discord_id, username, discriminator, global_name, avatar FROM user_discords WHERE user_id = ?",
                                      (user.id,)) as cursor:
                    discord_row = await cursor.fetchone()
                    if discord_row is not None:
                        discord = Discord(*discord_row)

            name_changes: list[PlayerNameChange] = []
            async with db.execute("SELECT id, name, date, approval_status FROM player_name_edit_requests WHERE player_id = ? AND approval_status != 'denied'", (self.id,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    request_id, request_name, request_date, request_approval = row
                    name_changes.append(PlayerNameChange(request_id, request_name, request_date, request_approval))

            return PlayerDetailed(self.id, name, country_code, bool(is_hidden), bool(is_shadow), bool(is_banned), discord, friend_codes, rosters, ban_info, user_settings, name_changes)
        
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

            append_equal_filter(filter.country, "p.country_code")
            append_equal_filter(filter.is_hidden, "p.is_hidden")
            append_equal_filter(filter.is_shadow, "p.is_shadow")
            append_equal_filter(filter.is_banned, "p.is_banned")
            append_equal_filter(filter.discord_id, "d.discord_id")

            # make sure that player is in a team roster which is linked to the passed-in squad ID
            if filter.squad_id is not None:
                where_clauses.append(f"""p.id IN (
                                     SELECT m.player_id FROM team_members m
                                     JOIN team_squad_registrations r ON r.roster_id = m.roster_id
                                     WHERE r.squad_id IS ? AND m.leave_date IS ?
                )""")
                variable_parameters.append(filter.squad_id)
                variable_parameters.append(None)

            # some filters require us to check if a player has a matching friend code,
            # so we do that here
            if filter.friend_code or filter.name_or_fc or filter.game:

                if filter.friend_code is not None:
                    fc_where_clauses.append("fc LIKE ?")
                    variable_parameters.append(f"%{filter.friend_code}%")

                # check names and friend codes
                if filter.name_or_fc:
                    fc_where_clauses.append("(f.fc LIKE ? OR p2.name LIKE ?)")
                    variable_parameters.append(f"%{filter.name_or_fc}%")
                    variable_parameters.append(f"%{filter.name_or_fc}%")

                if filter.game is not None:
                    fc_where_clauses.append("f.game = ?")
                    variable_parameters.append(filter.game)

                fc_where_clauses_str = ' AND '.join(fc_where_clauses)
                where_clauses.append(f"p.id IN (SELECT p2.id FROM players p2 LEFT JOIN friend_codes f ON p2.id = f.player_id WHERE {fc_where_clauses_str})")

            player_where_clause = "" if not where_clauses else f" WHERE {' AND '.join(where_clauses)}"
            players_query = f"""SELECT p.id, p.name, p.country_code, p.is_hidden, p.is_shadow, p.is_banned,
                                    d.discord_id, d.username, d.discriminator, d.global_name, d.avatar
                                    FROM players p
                                    LEFT JOIN users u ON u.player_id = p.id
                                    LEFT JOIN user_discords d ON u.id = d.user_id
                                    {player_where_clause} ORDER BY name COLLATE NOCASE LIMIT ? OFFSET ? """

            fc_where_clause = ""
            fc_where_clauses = []
            fc_variable_parameters: list[Any] = []
            # for player search, we want to return only the FCs with matching game and/or fc that we typed in
            if filter.detailed and filter.matching_fcs_only:
                if filter.game is not None:
                    fc_where_clauses.append("f.game = ?")
                    fc_variable_parameters.append(filter.game)
                if filter.friend_code:
                    fc_where_clauses.append("f.fc LIKE ?")
                    fc_variable_parameters.append(f"%{filter.friend_code}%")
                if filter.name_or_fc:
                    match = re.fullmatch(r"\d{4}-\d{4}-\d{4}", filter.name_or_fc)
                    if match:
                        fc_where_clauses.append("f.fc LIKE ?")
                        fc_variable_parameters.append(f"%{filter.name_or_fc}%")
                fc_where_clause = "" if not len(fc_where_clauses) else f"AND {' AND '.join(fc_where_clauses)}"
            friend_codes_query = f"""SELECT f.id, f.fc, f.game, f.player_id, f.is_verified, f.is_primary, f.description, f.is_active FROM friend_codes f WHERE f.player_id IN (
                SELECT p.id FROM players p
                LEFT JOIN users u ON u.player_id = p.id
                LEFT JOIN user_discords d ON u.id = d.user_id
                {player_where_clause} {fc_where_clause} LIMIT ? OFFSET ?
            )"""

            count_query = f"""SELECT COUNT (*) FROM (SELECT p.id FROM players p
                                    LEFT JOIN users u ON u.player_id = p.id
                                    LEFT JOIN user_discords d ON u.id = d.user_id
                                    {player_where_clause})"""

            players: List[PlayerDetailed] = []
            friend_codes: dict[int, list[FriendCode]] = {}

            # print(players_query)
            async with db.execute(players_query, (*variable_parameters, limit, offset)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    (id, name, country_code, is_hidden, is_shadow, is_banned, discord_id, d_username,
                     d_discriminator, d_global_name, d_avatar) = row
                    player_discord = None
                    if discord_id:
                        player_discord = Discord(discord_id, d_username, d_discriminator, d_global_name, d_avatar)
                    player = PlayerDetailed(id, name, country_code, is_hidden, is_shadow, is_banned, player_discord, [], [], None, None, [])
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
                        id, fc, game, player_id, is_verified, is_primary, description, is_active = row
                        friend_codes[player_id].append(FriendCode(id, fc, game, player_id, bool(is_verified), bool(is_primary), description, bool(is_active)))
                
            return PlayerList(players, player_count, page_count)

@save_to_command_log
@dataclass
class RequestEditPlayerNameCommand(Command[None]):
    player_id: int
    name: str

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT name FROM players WHERE id = ?", (self.player_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Player not found", status=404)
                curr_name = row[0]
                if curr_name == self.name:
                    raise Problem("Name must be different than current name", status=400)
            async with db.execute("SELECT date FROM player_name_edit_requests WHERE player_id = ? AND date > ? AND approval_status != 'denied' LIMIT 1",
                                    (self.player_id, (datetime.now(timezone.utc)-timedelta(days=90)).timestamp())) as cursor:
                row = await cursor.fetchone()
                if row:
                    raise Problem("Player has requested name change in the last 90 days", status=400)
            creation_date = int(datetime.now(timezone.utc).timestamp())
            await db.execute("INSERT INTO player_name_edit_requests(player_id, name, date, approval_status) VALUES (?, ?, ?, ?)", 
                             (self.player_id, self.name, creation_date, "pending"))
            await db.commit()
                    
@dataclass
class ListPlayerNameRequestsCommand(Command[list[PlayerNameRequest]]):
    approval_status: Approval

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            name_requests: list[PlayerNameRequest] = []
            async with db.execute("""SELECT p.id, p.name, p.country_code, r.id, r.name, r.date, r.approval_status
                                    FROM player_name_edit_requests r
                                    JOIN players p ON r.player_id = p.id
                                    WHERE r.approval_status = ?""", (self.approval_status,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    player_id, player_name, player_country, request_id, request_name, date, approval_status = row
                    name_requests.append(PlayerNameRequest(request_id, player_id, player_name, player_country, request_name, date, approval_status))
        return name_requests
    
@save_to_command_log
@dataclass
class ApprovePlayerNameRequestCommand(Command[None]):
    request_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT player_id, name FROM player_name_edit_requests WHERE id = ?", (self.request_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Name edit request not found", status=400)
                player_id, name = row
            await db.execute("UPDATE players SET name = ? WHERE id = ?", (name, player_id))
            await db.execute("UPDATE player_name_edit_requests SET approval_status = 'approved' WHERE id = ?", (self.request_id,))
            await db.commit()

@save_to_command_log
@dataclass
class DenyPlayerNameRequestCommand(Command[None]):
    request_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("UPDATE player_name_edit_requests SET approval_status = 'denied' WHERE id = ?", (self.request_id,)) as cursor:
                rowcount = cursor.rowcount
                if rowcount == 0:
                    raise Problem("Name edit request not found", status=404)
                await db.commit()

@dataclass
class GetPlayerTransferHistoryCommand(Command[PlayerTransferHistory]):
    player_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        history: list = []
        async with db_wrapper.connect(readonly=True) as db:
            # Unique composite key to identify joining team x at time t
            transfer_record_dict: dict[tuple[int, int], PlayerTransferItem] = {}
            async with db.execute('''SELECT 
                t.id, t.name as "team_name", tt.roster_id, tr.name as "roster_name", tt.roster_leave_id, tt.date, tt.is_accepted, tt.is_bagger_clause
                FROM team_transfers as tt
                JOIN team_rosters as tr
                ON tt.roster_id = tr.id
                JOIN teams as t
                ON t.id = tr.team_id
                WHERE player_id = ?
                ORDER BY tt.date DESC;''',
                (self.player_id,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    team_id, team_name, roster_id, roster_name, roster_leave_id, join_date, is_accepted, is_bagger_clause = row
                    transfer_record_dict[(roster_id, join_date)] = PlayerTransferItem(team_id, team_name, roster_id, roster_name, roster_leave_id, join_date, None, is_accepted, is_bagger_clause)

                    # NOTE: maybe I can move the finding leave date up here?
                    # if i sort in descending date order, we always have a transfer from the next record
                    # unless someone left a team, waited a year, then joined a new team... hmm

                for key, record in transfer_record_dict.items():
                    # don't care if we never left the team
                    # add the record and go next
                    if record.roster_leave_id is None:
                        history.append(record)
                        continue
                    # if we abandoned this team to join another, try to get the leave date
                    unique_transfer: tuple[int, int] = (record.roster_leave_id, record.join_date)

                    # if the abandoned team exists in the dict, update the leave date with the new team join date
                    # NOTE: but date is a timestamp, so how do i solve this....
                    if (unique_transfer) in transfer_record_dict.keys():
                        curr = transfer_record_dict[unique_transfer]
                        history.append(PlayerTransferItem(curr.team_id, curr.team_name, curr.roster_id, curr.roster_name, curr.roster_leave_id, curr.join_date, record.join_date, curr.is_accepted, curr.is_bagger_clause))

                results = PlayerTransferHistory(history)
                return results

