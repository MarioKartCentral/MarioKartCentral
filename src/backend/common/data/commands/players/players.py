import re
from common.data.command import Command
from common.data.db import DBWrapper
from common.data.models import *
from datetime import datetime, timezone

@dataclass
class CreatePlayerCommand(Command[Player]):
    user_id: int | None
    name: str
    country_code: CountryCode
    friend_codes: list[CreateFriendCodeRequestData]
    is_hidden: bool = False
    is_shadow: bool = False

    async def handle(self, db_wrapper: DBWrapper):
        name = self.name.strip()
        if len(name) < 2:
            raise Problem("Player name must be at least 2 characters", status=400)
        if len(name) > 24:
            raise Problem("Player name must be 24 characters or less", status=400)
        async with db_wrapper.connect(db_name="main", attach=["auth"]) as db:
            if self.user_id is not None:
                check_confirmed_email_query = """
                    SELECT player_id, ua.email_confirmed 
                    FROM users u
                    JOIN user_auth ua on u.id = ua.user_id
                    WHERE u.id = ?
                """
                async with db.execute(check_confirmed_email_query, (self.user_id,)) as cursor:
                    row = await cursor.fetchone()
                    assert row is not None
                    player_id, email_confirmed = row
                    if not bool(email_confirmed):
                        raise Problem("You must confirm your email to complete the player signup")
                    if player_id is not None:
                        raise Problem("Can only have one player per user", status=400)
            now = int(datetime.now(timezone.utc).timestamp())
            command = """INSERT INTO players(name, country_code, is_hidden, is_shadow, is_banned, join_date) 
                VALUES (?, ?, ?, ?, ?, ?)"""
            player_row = await db.execute_insert(
                command, 
                (name, self.country_code, self.is_hidden, self.is_shadow, False, now))
            
            # TODO: Run queries to determine why it errored
            if player_row is None:
                raise Problem("Failed to create player")
            
            player_id = player_row[0]

            if self.user_id is not None:
                async with db.execute("UPDATE users SET player_id = ? WHERE id = ?", (player_id, self.user_id)) as cursor:
                    # handle case where user with the given ID doesn't exist
                    if cursor.rowcount != 1:
                        raise Problem("Invalid User ID", status=404)
                    
            fc_set = set([friend_code.fc for friend_code in self.friend_codes])
            if len(fc_set) < len(self.friend_codes):
                raise Problem("Cannot have duplicate FCs", status=400)
            fc_limits: dict[FriendCodeType, int] = {"switch": 1, "mkt": 1, "mkw": 4, "3ds": 1, "nnid": 1}
            for type in fc_limits.keys():
                game_fcs = [fc for fc in self.friend_codes if fc.type == type]
                if len(game_fcs) > fc_limits[type]:
                    raise Problem(f"Too many friend codes were provided for the FC type {type} (limit {fc_limits[type]})", status=400)
                    
            for friend_code in self.friend_codes:
                match = re.fullmatch(r"\d{4}-\d{4}-\d{4}", friend_code.fc)
                if friend_code.type != "nnid" and not match:
                    raise Problem(f"FC {friend_code.fc} of type {friend_code.type} is in incorrect format", status=400)
                if friend_code.type == "nnid" and len(friend_code.fc) > 16:
                    raise Problem("NNIDs must be 16 characters or less", status=400)
                
                # check if friend code is currently in use
                async with db.execute("SELECT id FROM friend_codes WHERE fc = ? AND type = ? AND is_active = ?", (friend_code.fc, friend_code.type, True)) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        raise Problem(f"Another player is currently using this {friend_code.type} friend code", status=400)
                    
            friend_code_tuples = [(player_id, friend_code.type, friend_code.fc, False, friend_code.is_primary, True, friend_code.description, now)
                                  for friend_code in self.friend_codes]
            await db.executemany("INSERT INTO friend_codes(player_id, type, fc, is_verified, is_primary, is_active, description, creation_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    friend_code_tuples)
            await db.commit()
            return Player(int(player_id), name, self.country_code, self.is_hidden, self.is_shadow, False, now, None)

@dataclass
class UpdatePlayerCommand(Command[bool]):
    data: EditPlayerRequestData
    mod_player_id: int

    async def handle(self, db_wrapper: DBWrapper) -> bool:
        data = self.data
        async with db_wrapper.connect() as db:
            if len(self.data.name) > 24:
                raise Problem("Player name must be 24 characters or less", status=400)
            async with db.execute("SELECT name FROM players WHERE id = ?", (data.player_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Player not found", status=404)
                curr_name = row[0]
            update_query = """UPDATE players 
            SET name = ?, country_code = ?, is_hidden = ?, is_shadow = ?
            WHERE id = ?"""
            params = (data.name.strip(), data.country_code, data.is_hidden, data.is_shadow, data.player_id)

            async with db.execute(update_query, params) as cursor:
                if cursor.rowcount != 1:
                    return False
            if curr_name != data.name:
                now = int(datetime.now(timezone.utc).timestamp())
                await db.execute("""INSERT INTO player_name_edits(player_id, old_name, new_name, date, approval_status, handled_by)
                                    VALUES(?, ?, ?, ?, ?, ?)""", (data.player_id, curr_name, data.name.strip(), now, "approved", self.mod_player_id))

            await db.commit()
            return True


@dataclass
class GetPlayerDetailedCommand(Command[PlayerDetailed | None]):
    id: int
    include_notes: bool = False
    include_unban_date: bool = False

    async def handle(self, db_wrapper: DBWrapper) -> PlayerDetailed | None:
        async with db_wrapper.connect(readonly=True) as db:
            query = "SELECT name, country_code, is_hidden, is_shadow, is_banned, join_date FROM players WHERE id = ?"
            async with db.execute(query, (self.id,)) as cursor:
                player_row = await cursor.fetchone()
            
            if player_row is None:
                return None
            
            name, country_code, is_hidden, is_shadow, is_banned, player_join_date = player_row

            fc_query = "SELECT id, type, fc, is_verified, is_primary, description, is_active, creation_date FROM friend_codes WHERE player_id = ?"
            friend_code_rows = await db.execute_fetchall(fc_query, (self.id, ))
            friend_codes = [FriendCode(id, fc, type, self.id, bool(is_verified), bool(is_primary), creation_date, description, bool(is_active)) for id, type, fc, is_verified, is_primary, 
                            description, is_active, creation_date in friend_code_rows]

            user_query = "SELECT id FROM users WHERE player_id = ?"
            async with db.execute(user_query, (self.id,)) as cursor:
                user_row = await cursor.fetchone()
            
            user = None if user_row is None else User(int(user_row[0]), self.id)

            rosters: list[PlayerRoster] = []
            async with db.execute("""SELECT m.roster_id, m.join_date, t.id, t.name, t.tag, t.color, r.name, r.tag, r.game, r.mode, m.is_bagger_clause
                                    FROM team_members m
                                    JOIN team_rosters r ON m.roster_id = r.id
                                    JOIN teams t ON r.team_id = t.id
                                    WHERE m.player_id = ? AND m.leave_date IS NULL
                                    AND t.approval_status = 'approved'""", (self.id,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    roster_id, join_date, team_id, team_name, team_tag, color, roster_name, roster_tag, game, mode, is_bagger_clause = row
                    roster_name = roster_name if roster_name else team_name
                    roster_tag = roster_tag if roster_tag else team_tag
                    rosters.append(PlayerRoster(roster_id, join_date, team_id, team_name, team_tag, color, roster_name, roster_tag, game, mode, bool(is_bagger_clause)))

            ban_info = None
            if is_banned:
                ban_query = """SELECT reason, expiration_date, is_indefinite FROM player_bans WHERE player_id = ?"""
                async with db.execute(ban_query, (self.id,)) as cursor:
                    ban_row = await cursor.fetchone()
                unban_date = ban_row[1] if ban_row and self.include_unban_date else None
                is_indefinite = ban_row[2] if ban_row and self.include_unban_date else None
                ban_info = None if ban_row is None else PlayerBanBasic(self.id, ban_row[0], unban_date, is_indefinite)

            user_settings = None
            if user:
                async with db.execute("""SELECT avatar, about_me, language, 
                    color_scheme, timezone, hide_discord FROM user_settings WHERE user_id = ?""", (user.id,)) as cursor:
                    settings_row = await cursor.fetchone()
                    if settings_row is not None:
                        avatar, about_me, language, color_scheme, timezone, hide_discord = settings_row
                        user_settings = UserSettings(user.id, avatar, about_me, language, color_scheme, timezone, bool(hide_discord))

            discord = None
            if user:
                async with db.execute("SELECT discord_id, username, discriminator, global_name, avatar FROM user_discords WHERE user_id = ?",
                                      (user.id,)) as cursor:
                    discord_row = await cursor.fetchone()
                    if discord_row is not None:
                        discord = Discord(*discord_row)

            name_changes: list[PlayerNameChange] = []
            async with db.execute("SELECT id, old_name, new_name, date, approval_status FROM player_name_edits WHERE player_id = ? AND approval_status != 'denied'", (self.id,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    request_id, old_name, new_name, request_date, request_approval = row
                    name_changes.append(PlayerNameChange(request_id, old_name, new_name, request_date, request_approval))

            notes = None
            if self.include_notes:
                # Connect to main database and attach player_notes
                async with db_wrapper.connect(db_name='main', attach=['player_notes']) as db_with_notes:
                    async with db_with_notes.execute("SELECT notes, edited_by, date FROM player_notes.player_notes WHERE player_id = ?", (self.id,)) as cursor:
                        row = await cursor.fetchone()
                        if row:
                            player_notes, edited_by, date = row
                            query = """SELECT p.id, p.name, p.country_code, p.is_hidden, p.is_shadow, p.is_banned, p.join_date FROM players p 
                                JOIN users u ON u.player_id = p.id
                                WHERE u.id = ?"""
                            async with db_with_notes.execute(query, (edited_by,)) as cursor:
                                player_row = await cursor.fetchone()
                                edited_by = None
                                if player_row:
                                    p_id, p_name, p_country_code, p_is_hidden, p_is_shadow, p_is_banned, p_join_date = player_row
                                    edited_by = Player(p_id, p_name, p_country_code, p_is_hidden, p_is_shadow, p_is_banned, p_join_date, None)
                                notes = PlayerNotes(player_notes, edited_by, date)

            roles: list[PlayerRole] = []
            if user:
                async with db.execute("""SELECT r.id, r.name, r.position
                                        FROM roles r
                                        JOIN user_roles ur ON r.id = ur.role_id
                                        WHERE ur.user_id = ?
                                        ORDER BY r.position""", (user.id,)) as cursor:
                    rows = await cursor.fetchall()
                    for row in rows:
                        role_id, role_name, role_position = row
                        roles.append(PlayerRole(role_id, role_name, role_position))

            return PlayerDetailed(self.id, name, country_code, bool(is_hidden), bool(is_shadow), bool(is_banned), player_join_date, discord, friend_codes, 
                                  rosters, ban_info, user_settings, name_changes, notes, roles)
        
@dataclass
class ListPlayersCommand(Command[PlayerList]):
    filter: PlayerFilter

    async def handle(self, db_wrapper: DBWrapper) -> PlayerList:
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
            if filter.registration_id is not None:
                where_clauses.append(f"""p.id IN (
                                     SELECT m.player_id FROM team_members m
                                     JOIN team_squad_registrations r ON r.roster_id = m.roster_id
                                     WHERE r.registration_id IS ? AND m.leave_date IS ?
                )""")
                variable_parameters.append(filter.registration_id)
                variable_parameters.append(None)

            # if has_connected_user is true, we should only list players who have
            # a user connected to them.
            # if it's false, we only want players who do not have a user connected to them.
            if filter.has_connected_user is not None:
                if filter.has_connected_user:
                    where_clauses.append("""p.id IN (
                                            SELECT u.player_id FROM users u
                                            WHERE u.player_id IS NOT NULL
                                         )""")
                else:
                    where_clauses.append("""p.id NOT IN (
                                            SELECT u.player_id FROM users u
                                            WHERE u.player_id IS NOT NULL
                                        )""")

            # some filters require us to check if a player has a matching friend code,
            # so we do that here
            if filter.friend_code or filter.name_or_fc or filter.fc_type:

                if filter.friend_code is not None:
                    fc_where_clauses.append("fc LIKE ?")
                    variable_parameters.append(f"%{filter.friend_code}%")

                # check names and friend codes
                if filter.name_or_fc:
                    fc_where_clauses.append("(f.fc LIKE ? OR p2.name LIKE ?)")
                    variable_parameters.append(f"%{filter.name_or_fc}%")
                    variable_parameters.append(f"%{filter.name_or_fc}%")

                if filter.fc_type is not None:
                    # used when manually registering players for a tournament,
                    # includes shadow players in the results even if they don't have an
                    # FC for the type in the filter
                    if filter.include_shadow_players:
                        fc_where_clauses.append("(f.type = ? OR p2.is_shadow = 1)")
                    else:
                        fc_where_clauses.append("f.type = ?")
                    variable_parameters.append(filter.fc_type)

                fc_where_clauses_str = ' AND '.join(fc_where_clauses)
                where_clauses.append(f"p.id IN (SELECT p2.id FROM players p2 LEFT JOIN friend_codes f ON p2.id = f.player_id WHERE {fc_where_clauses_str})")

            player_where_clause = "" if not where_clauses else f" WHERE {' AND '.join(where_clauses)}"
            order_by = 'p.join_date' if filter.sort_by_newest else 'name'
            desc = 'DESC' if filter.sort_by_newest else ''
            player_from_where_clause = f"{player_where_clause} ORDER BY {order_by} COLLATE NOCASE {desc} LIMIT ? OFFSET ?"
            players_query = f"""SELECT p.id, p.name, p.country_code, p.is_hidden, p.is_shadow, p.is_banned, p.join_date,
                                    d.discord_id, d.username, d.discriminator, d.global_name, d.avatar
                                    FROM players p
                                    LEFT JOIN users u ON u.player_id = p.id
                                    LEFT JOIN user_discords d ON u.id = d.user_id
                                    {player_from_where_clause}"""

            fc_where_clause = ""
            fc_where_clauses = []
            fc_variable_parameters: list[Any] = []
            # for player search, we want to return only the FCs with matching type and/or fc that we typed in
            if filter.detailed and filter.matching_fcs_only:
                if filter.fc_type is not None:
                    fc_where_clauses.append("f.type = ?")
                    fc_variable_parameters.append(filter.fc_type)
                if filter.friend_code:
                    fc_where_clauses.append("f.fc LIKE ?")
                    fc_variable_parameters.append(f"%{filter.friend_code}%")
                if filter.name_or_fc:
                    match = re.fullmatch(r"\d{4}-\d{4}-\d{4}", filter.name_or_fc)
                    if match:
                        fc_where_clauses.append("f.fc LIKE ?")
                        fc_variable_parameters.append(f"%{filter.name_or_fc}%")
                fc_where_clause = "" if not len(fc_where_clauses) else f"AND {' AND '.join(fc_where_clauses)}"
            friend_codes_query = f"""SELECT f.id, f.fc, f.type, f.player_id, f.is_verified, f.is_primary, f.description, f.is_active, f.creation_date FROM friend_codes f WHERE f.player_id IN (
                SELECT p.id FROM players p
                LEFT JOIN users u ON u.player_id = p.id
                LEFT JOIN user_discords d ON u.id = d.user_id
                {player_from_where_clause}
            ) {fc_where_clause}"""

            count_query = f"""SELECT COUNT (*) FROM (SELECT p.id FROM players p
                                    LEFT JOIN users u ON u.player_id = p.id
                                    LEFT JOIN user_discords d ON u.id = d.user_id
                                    {player_where_clause})"""

            players: list[PlayerDetailed] = []
            friend_codes: dict[int, list[FriendCode]] = {}

            async with db.execute(players_query, (*variable_parameters, limit, offset)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    (id, name, country_code, is_hidden, is_shadow, is_banned, join_date, discord_id, d_username,
                     d_discriminator, d_global_name, d_avatar) = row
                    player_discord = None
                    if discord_id:
                        player_discord = Discord(discord_id, d_username, d_discriminator, d_global_name, d_avatar)
                    player = PlayerDetailed(id, name, country_code, is_hidden, is_shadow, is_banned, join_date, player_discord, [], [], None, None, [], None, [])
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
                async with db.execute(friend_codes_query, (*variable_parameters, limit, offset, *fc_variable_parameters)) as cursor:
                    rows = await cursor.fetchall()
                    for row in rows:
                        id, fc, fc_type, player_id, is_verified, is_primary, description, is_active, creation_date = row
                        friend_codes[player_id].append(FriendCode(id, fc, fc_type, player_id, bool(is_verified), bool(is_primary), creation_date, description, bool(is_active)))
                
            return PlayerList(players, player_count, page_count)

@dataclass
class MergePlayersCommand(Command[None]):
    from_player_id: int
    to_player_id: int

    async def handle(self, db_wrapper: DBWrapper):
        if self.from_player_id == self.to_player_id:
            raise Problem("Player IDs are equal", status=400)
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT id FROM players WHERE id = ?", (self.from_player_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem(f"Player with ID {self.from_player_id} not found", status=404)
            async with db.execute("SELECT id FROM players WHERE id = ?", (self.to_player_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem(f"Player with ID {self.to_player_id} not found", status=404)
                
            # merge the old player's info into the new player
            await db.execute("UPDATE friend_codes SET player_id = ? WHERE player_id = ?", (self.to_player_id, self.from_player_id))
            await db.execute("UPDATE tournament_players SET player_id = ? WHERE player_id = ?", (self.to_player_id, self.from_player_id))
            await db.execute("UPDATE team_members SET player_id = ? WHERE player_id = ?", (self.to_player_id, self.from_player_id))
            await db.execute("UPDATE team_transfers SET player_id = ? WHERE player_id = ?", (self.to_player_id, self.from_player_id))
            await db.execute("UPDATE player_bans SET player_id = ? WHERE player_id = ?", (self.to_player_id, self.from_player_id))
            await db.execute("UPDATE player_bans_historical SET player_id = ? WHERE player_id = ?", (self.to_player_id, self.from_player_id))
            await db.execute("UPDATE player_name_edits SET player_id = ? WHERE player_id = ?", (self.to_player_id, self.from_player_id))
            await db.execute("UPDATE users SET player_id = ? WHERE player_id = ?", (None, self.from_player_id))
            await db.execute("DELETE FROM players WHERE id = ?", (self.from_player_id,))
            await db.commit()

@dataclass
class GetPlayerTransferHistoryCommand(Command[PlayerTransferHistory]):
    player_id: int

    async def handle(self, db_wrapper: DBWrapper):
        history: list[PlayerTransferItem] = []
        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute('''SELECT t.id, t.name as "team_name", tr.game, tr.mode, tm.join_date, tm.leave_date, tm.is_bagger_clause, tr.name as "roster_name"
                FROM team_members as tm
                JOIN team_rosters as tr
                ON tm.roster_id = tr.id
                JOIN teams as t
                ON t.id = tr.team_id
                WHERE player_id = ?
                AND t.approval_status="approved"
                ORDER BY tm.join_date ASC;''',
                (self.player_id,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    team_id, team_name, game, mode, join_date, leave_date, is_bagger_clause, roster_name = row
                    history.append(PlayerTransferItem(team_id, team_name, game, mode, join_date, leave_date, bool(is_bagger_clause), roster_name))
                results = PlayerTransferHistory(history)
                return results
