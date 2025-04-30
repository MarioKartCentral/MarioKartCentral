from dataclasses import dataclass
from datetime import timedelta, timezone
from common.auth import team_permissions, team_roles
from common.data.commands import Command, save_to_command_log
from common.data.models import *

@dataclass
class ViewRosterEditHistoryCommand(Command[list[RosterEdit]]):
    team_id: int
    roster_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        edits: list[RosterEdit] = []
        async with db_wrapper.connect() as db:
            async with db.execute("""SELECT re.id, re.roster_id, re.old_name, re.new_name, re.old_tag, re.new_tag, re.date, re.approval_status,
                                  t.color, t.id, re.handled_by, p.name, p.country_code 
                                  FROM roster_edits re JOIN team_rosters r ON re.roster_id = r.id
                                  JOIN teams t ON r.team_id = t.id
                                  LEFT JOIN players p ON re.handled_by = p.id
                                  WHERE re.roster_id = ? AND re.approval_status != ?""",
                                  (self.roster_id, "denied")) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    (request_id, roster_id, old_name, new_name, old_tag, new_tag, date, 
                     approval_status, color, team_id, handled_by_id, handled_by_name, handled_by_country) = row
                    handled_by = None
                    if handled_by_id:
                        handled_by = PlayerBasic(handled_by_id, handled_by_name, handled_by_country)
                    edits.append(RosterEdit(request_id, roster_id, team_id, old_name, old_tag, new_name, new_tag, color, date, approval_status, handled_by))
        return edits
    
@save_to_command_log
@dataclass
class CreateRosterCommand(Command[None]):
    team_id: int
    game: str
    mode: str
    name: str | None
    tag: str | None
    is_recruiting: bool
    is_active: bool
    approval_status: Approval

    async def handle(self, db_wrapper, s3_wrapper):
        if self.name:
            self.name = self.name.strip()
        if self.tag:
            self.tag = self.tag.strip()
        if self.name and len(self.name) > 32:
            raise Problem("Roster name must be 32 characters or less", status=400)
        if self.tag and len(self.tag) > 5:
            raise Problem("Roster tag must be 5 characters or less", status=400)
        async with db_wrapper.connect() as db:
            valid_game_modes = {"mk8dx": ["150cc", "200cc"],
                                "mkw": ["rt", "ct"],
                                "mkt": ["vsrace"],
                                "mkworld": ["150cc", "200cc"],}
            if self.game not in valid_game_modes:
                raise Problem(f"Invalid game (valid games: {', '.join(valid_game_modes.keys())})", status=400)
            if self.mode not in valid_game_modes[self.game]:
                raise Problem(f"Invalid mode (valid modes: {', '.join(valid_game_modes[self.game])})", status=400)
            # get team name and tag
            async with db.execute("SELECT name, tag, approval_status FROM teams WHERE id = ?", (self.team_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem('No team found', status=404)
                team_name, team_tag, team_approval = row
                if team_approval != 'approved':
                    raise Problem('Cannot create roster if team is not approved')
            # set name and tag to None if they are equal to main team so that they change if the team does
            if self.name == team_name:
                self.name = None
            if self.tag == team_tag:
                self.tag = None
            # check to make sure we aren't making 2 rosters with the same name
            async with db.execute("SELECT name FROM team_rosters WHERE team_id = ? AND game = ? AND mode = ? AND name IS ?", (self.team_id, self.game, self.mode, self.name)) as cursor:
                row = await cursor.fetchone()
                if row is not None:
                    raise Problem('Only one roster per game/mode may use the same name', status=400)
            creation_date = int(datetime.now(timezone.utc).timestamp())
            await db.execute("""INSERT INTO team_rosters(team_id, game, mode, name, tag, creation_date, is_recruiting, is_active, approval_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", (self.team_id, self.game, self.mode, self.name, self.tag, creation_date, self.is_recruiting, self.is_active, self.approval_status))
            await db.commit()

@save_to_command_log     
@dataclass
class EditRosterCommand(Command[None]):
    roster_id: int
    team_id: int
    name: str
    tag: str
    is_recruiting: bool
    is_active: bool
    approval_status: Approval
    mod_player_id: int | None

    async def handle(self, db_wrapper, s3_wrapper):
        self.name = self.name.strip()
        self.tag = self.tag.strip()
        if self.name and len(self.name) > 32:
            raise Problem("Roster name must be 32 characters or less", status=400)
        if self.tag and len(self.tag) > 5:
            raise Problem("Roster tag must be 5 characters or less", status=400)
        async with db_wrapper.connect() as db:
            # get team name and tag
            async with db.execute("SELECT name, tag, approval_status FROM teams WHERE id = ?", (self.team_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem('No team found', status=404)
                team_name, team_tag, team_approval = row
                if team_approval != "approved" and self.approval_status == "approved":
                    raise Problem("Team must be approved for roster to be approved")
            # set name and tag to None if they are equal to main team so that they change if the team does
            name = self.name
            tag = self.tag
            if self.name == team_name:
                name = None
            if self.tag == team_tag:
                tag = None
            # get the current roster's name and check if it exists
            async with db.execute("SELECT name, tag, game, mode FROM team_rosters WHERE id = ? AND team_id = ?", (self.roster_id, self.team_id)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem('No roster found')
                roster_name, roster_tag, game, mode = row
            if roster_name != name:
                # check to make sure another roster doesn't have the name we're changing to
                async with db.execute("SELECT name FROM team_rosters WHERE team_id = ? AND game = ? AND mode = ? AND name IS ? AND id != ?", (self.team_id, game, mode, name, self.roster_id)) as cursor:
                    row = await cursor.fetchone()
                    if row is not None:
                        raise Problem('Only one roster per game/mode may use the same name', status=400)
            if roster_name != name or roster_tag != tag:
                now = int(datetime.now(timezone.utc).timestamp())
                old_name = roster_name if roster_name else team_name
                old_tag = roster_tag if roster_tag else team_tag
                await db.execute("""INSERT INTO roster_edits(roster_id, old_name, new_name, old_tag, new_tag, date, approval_status, handled_by)
                                    VALUES(?, ?, ?, ?, ?, ?, ?, ?)""", (self.roster_id, old_name, self.name, old_tag, self.tag, now, "approved", self.mod_player_id))
            await db.execute("""UPDATE team_rosters SET team_id = ?, name = ?, tag = ?, is_recruiting = ?, is_active = ?, approval_status = ?
                                WHERE id = ?""",
                             (self.team_id, name, tag, self.is_recruiting, self.is_active, self.approval_status, self.roster_id))
            await db.commit()

@save_to_command_log
@dataclass
class ManagerEditRosterCommand(Command[None]):
    roster_id: int
    team_id: int
    is_recruiting: bool

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("UPDATE team_rosters SET is_recruiting = ? WHERE id = ? AND team_id = ?", (self.is_recruiting, self.roster_id, self.team_id)) as cursor:
                rows = cursor.rowcount
                if not rows:
                    raise Problem("Roster not found", status=404)
                await db.commit()


@save_to_command_log
@dataclass
class LeaveRosterCommand(Command[None]):
    player_id: int
    roster_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT id FROM team_members WHERE player_id = ? AND roster_id = ? AND leave_date IS ?", (self.player_id, self.roster_id, None)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem("Player is not currently on this roster", status=400)
                team_member_id = row[0]
            leave_date = int(datetime.now(timezone.utc).timestamp())
            await db.execute("UPDATE team_members SET leave_date = ? WHERE id = ?", (leave_date, team_member_id))
            # players leaving a roster goes into the transfer history too
            await db.execute("""INSERT INTO team_transfers(player_id, roster_id, date, roster_leave_id, is_accepted, approval_status, is_bagger_clause)
                             VALUES (?, ?, ?, ?, ?, ?, ?)""", (self.player_id, None, leave_date, self.roster_id, True, "approved", False))
            # get all team tournament rosters the player is in where the tournament hasn't ended yet
            async with db.execute("""SELECT p.registration_id FROM tournament_players p
                                JOIN team_squad_registrations s ON p.registration_id = s.registration_id
                                JOIN tournaments t ON p.tournament_id = t.id
                                WHERE p.player_id = ? AND s.roster_id = ?
                                AND (t.date_end > ? OR t.registrations_open = ?) AND t.team_members_only = ?""",
                                (self.player_id, self.roster_id, leave_date, True, True)) as cursor:
                rows = await cursor.fetchall()
                registration_ids: list[int] = [row[0] for row in rows]
            # finally remove the player from all the tournaments they shouldn't be in
            await db.execute(f"DELETE FROM tournament_players WHERE player_id = ? AND registration_id IN ({','.join(map(str, registration_ids))})", (self.player_id,))
            await db.commit()

@save_to_command_log
@dataclass
class RequestEditRosterCommand(Command[None]):
    roster_id: int
    team_id: int
    name: str
    tag: str

    async def handle(self, db_wrapper, s3_wrapper):
        if len(self.name) > 32:
            raise Problem("Roster name must be 32 characters or less", status=400)
        if len(self.tag) > 5:
            raise Problem("Roster tag must be 5 characters or less", status=400)
        name = self.name.strip()
        tag = self.tag.strip()
        async with db_wrapper.connect() as db:
            # check if this roster has made a request in the last 90 days
            async with db.execute("SELECT date FROM roster_edits WHERE roster_id = ? AND date > ? AND approval_status != 'denied' LIMIT 1",
                                  (self.roster_id, (datetime.now(timezone.utc)-timedelta(days=90)).timestamp())) as cursor:
                row = await cursor.fetchone()
                if row:
                    raise Problem("Roster has requested name/tag change in the last 90 days", status=400)
            async with db.execute("SELECT t.name, t.tag, r.name, r.tag, r.game, r.mode, r.approval_status FROM team_rosters r JOIN teams t ON r.team_id = t.id WHERE r.id = ? AND r.team_id = ?", (self.roster_id, self.team_id)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Roster not found", status=404)
                team_name, team_tag, roster_name, roster_tag, game, mode, approval_status = row
                if approval_status != "approved":
                    raise Problem("Cannot request to edit roster if it is not approved")
                # sync roster name/tag with team if none
                if roster_name is None:
                    roster_name = team_name
                if roster_tag is None:
                    roster_tag = team_tag
                if name == roster_name and tag == roster_tag:
                    raise Problem("At least one of the roster name or tag must be different from their current values", status=400)
            async with db.execute("SELECT id FROM team_rosters WHERE id != ? AND team_id = ? AND game = ? AND mode = ? AND name IS ?",
                                (self.roster_id, self.team_id, game, mode, name)) as cursor:
                row = await cursor.fetchone()
                if row:
                    raise Problem("Another roster for this game and mode has the same name as the specified name", status=400)
            creation_date = int(datetime.now(timezone.utc).timestamp())
            await db.execute("INSERT INTO roster_edits(roster_id, old_name, new_name, old_tag, new_tag, date, approval_status) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                             (self.roster_id, roster_name, name, roster_tag, tag, creation_date, "pending"))
            await db.commit()

@save_to_command_log
@dataclass
class ApproveRosterCommand(Command[None]):
    team_id: int
    roster_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("""SELECT r.approval_status, t.approval_status
                                  FROM team_rosters r
                                  JOIN teams t ON r.team_id = t.id
                                  WHERE r.id = ? AND r.team_id = ?""", (self.roster_id, self.team_id)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Roster not found", status=404)
                roster_approved, team_approved = row
                if team_approved != "approved":
                    raise Problem("Team must be approved to approve/deny its rosters")
                if roster_approved == "approved":
                    raise Problem("Roster is already approved")
            await db.execute("UPDATE team_rosters SET approval_status = 'approved' WHERE id = ?", (self.roster_id,))
            await db.commit()

@save_to_command_log
@dataclass
class DenyRosterCommand(Command[None]):
    team_id: int
    roster_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("""SELECT r.approval_status, t.approval_status
                                  FROM team_rosters r
                                  JOIN teams t ON r.team_id = t.id
                                  WHERE r.id = ? AND r.team_id = ?""", (self.roster_id, self.team_id)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Roster not found", status=404)
                roster_approved, team_approved = row
                if team_approved != "approved":
                    raise Problem("Team must be approved to approve/deny its rosters")
                if roster_approved == "approved":
                    raise Problem("Roster is already approved")
            await db.execute("UPDATE team_rosters SET approval_status = 'denied' WHERE id = ?", (self.roster_id,))
            await db.commit()

@save_to_command_log
@dataclass
class ApproveRosterEditCommand(Command[None]):
    request_id: int
    mod_player_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("""SELECT r.roster_id, r.new_name, r.new_tag, t.name, t.tag 
                                  FROM roster_edits r
                                  JOIN team_rosters tr ON r.roster_id = tr.id
                                  JOIN teams t ON tr.team_id = t.id
                                  WHERE r.id = ?""", (self.request_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Roster edit request not found", status=404)
                roster_id, name, tag, team_name, team_tag = row
            if name == team_name:
                name = None
            if tag == team_tag:
                tag = None
            await db.execute("UPDATE team_rosters SET name = ?, tag = ? WHERE id = ?", (name, tag, roster_id))
            await db.execute("UPDATE roster_edits SET approval_status = 'approved', handled_by = ? WHERE id = ?", (self.mod_player_id, self.request_id))
            await db.commit()

@save_to_command_log
@dataclass
class DenyRosterEditCommand(Command[None]):
    request_id: int
    mod_player_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("UPDATE roster_edits SET approval_status = 'denied', handled_by = ? WHERE id = ?", (self.mod_player_id, self.request_id)) as cursor:
                rowcount = cursor.rowcount
                if rowcount == 0:
                    raise Problem("Roster edit request not found", status=404)
            await db.commit()

@dataclass
class ListRosterEditRequestsCommand(Command[RosterEditList]):
    filter: RosterEditFilter

    async def handle(self, db_wrapper, s3_wrapper):
        filter = self.filter
        requests: list[RosterEdit] = []
        limit = 20
        offset = 0
        if filter.page is not None:
            offset = (filter.page - 1) * limit

        async with db_wrapper.connect() as db:
            request_query = """FROM roster_edits re JOIN team_rosters r ON re.roster_id = r.id
                                JOIN teams t ON r.team_id = t.id
                                LEFT JOIN players p ON re.handled_by = p.id
                                WHERE re.approval_status = ?"""
            async with db.execute(f"""SELECT re.id, re.roster_id, re.old_name, re.new_name, re.old_tag, re.new_tag, re.date, re.approval_status,
                                  t.color, t.id, re.handled_by, p.name, p.country_code 
                                  {request_query} ORDER BY re.date LIMIT ? OFFSET ?""", (filter.approval_status, limit, offset)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    (request_id, roster_id, old_name, new_name, old_tag, new_tag, date, 
                     approval_status, color, team_id, handled_by_id, handled_by_name, handled_by_country) = row
                    handled_by = None
                    if handled_by_id:
                        handled_by = PlayerBasic(handled_by_id, handled_by_name, handled_by_country)
                    requests.append(RosterEdit(request_id, roster_id, team_id, old_name, old_tag, new_name, new_tag, color, date, approval_status, handled_by))

            count_query = f"SELECT COUNT(*) {request_query}"
            async with db.execute(count_query, (filter.approval_status,)) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                request_count = row[0]

            page_count = int(request_count / limit) + (1 if request_count % limit else 0)
        return RosterEditList(requests, request_count, page_count)
    
       
@dataclass
class ListRostersCommand(Command[list[TeamRoster]]):
    approved: bool = True

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            where_clauses: list[str] = []
            variable_parameters: list[Any] = []

            def append_equal_filter(filter_value: Any, column_name: str):
                if filter_value is not None:
                    where_clauses.append(f"{column_name} = ?")
                    variable_parameters.append(filter_value)

            def append_not_equal_filter(filter_value: Any, column_name: str):
                if filter_value is not None:
                    where_clauses.append(f"{column_name} != ?")
                    variable_parameters.append(filter_value)

            if self.approved:
                append_equal_filter("approved", "r.approval_status")
            else:
                # want unapproved rosters only for teams which havent been approved yet
                append_not_equal_filter("approved", "r.approval_status")
                append_equal_filter("approved", "t.approval_status")

            where_clause = "" if not where_clauses else f" WHERE {' AND '.join(where_clauses)}"
            rosters_query = f"""SELECT r.id, r.team_id, r.game, r.mode, r.name, r.tag,
                                        r.creation_date, r.is_recruiting, r.is_active, r.approval_status,
                                        t.name, t.tag, t.color
                                        FROM team_rosters r
                                        JOIN teams t ON r.team_id = t.id
                                        {where_clause}
                                        """
            rosters: list[TeamRoster] = []
            async with db.execute(rosters_query, variable_parameters) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    (roster_id, team_id, game, mode, roster_name, roster_tag, creation_date, is_recruiting,
                     is_active, approval_status, team_name, team_tag, team_color) = row
                    roster_name = roster_name if roster_name else team_name
                    roster_tag = roster_tag if roster_tag else team_tag
                    roster = TeamRoster(roster_id, team_id, game, mode, roster_name, roster_tag,
                                        creation_date, is_recruiting, is_active, approval_status, team_color, [], [])
                    rosters.append(roster)
            return rosters

@dataclass
class GetRegisterableRostersCommand(Command[list[TeamRoster]]):
    user_id: int
    tournament_id: int
    game: Game
    mode: GameMode
    
    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            rosters_query = """
                    FROM team_roles r
                    JOIN user_team_roles ur ON ur.role_id = r.id
                    JOIN team_rosters tr ON tr.team_id = ur.team_id
                    JOIN teams t ON tr.team_id = t.id
                    JOIN users u ON ur.user_id = u.id
                    JOIN team_role_permissions rp ON rp.role_id = r.id
                    JOIN team_permissions p ON rp.permission_id = p.id
                    WHERE u.id = ? AND p.name = ? AND tr.game = ? AND tr.mode = ?
                        AND tr.approval_status = ? AND tr.is_active = ?
                        AND tr.id NOT IN (
                            SELECT roster_id
                            FROM team_squad_registrations tsr
                            JOIN tournament_registrations s ON tsr.registration_id = s.id
                            WHERE tsr.tournament_id = ?
                            AND s.is_registered = ?
                        )"""
            variable_parameters = (self.user_id, team_permissions.REGISTER_TOURNAMENT, self.game, self.mode, "approved", True, self.tournament_id, True)
            rosters: list[TeamRoster] = []
            roster_dict: dict[int, list[RosterPlayerInfo]] = {}
            async with db.execute(f"""SELECT tr.id, tr.team_id, tr.game, tr.mode, tr.name, tr.tag, tr.creation_date,
                                  tr.is_recruiting, tr.is_active, tr.approval_status, t.name, t.tag, t.color
                                  {rosters_query}""",
                    variable_parameters) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    (roster_id, team_id, game, mode, roster_name, roster_tag, creation_date, is_recruiting, 
                     is_active, approval_status, team_name, team_tag, team_color) = row
                    roster_name = roster_name if roster_name else team_name
                    roster_tag = roster_tag if roster_tag else team_tag
                    roster = TeamRoster(roster_id, team_id, game, mode, roster_name, roster_tag,
                                        creation_date, is_recruiting, is_active, approval_status, team_color, [], [])
                    roster_dict[roster.id] = roster.players
                    rosters.append(roster)

            # get players for our rosters

            # use a set for O(1) lookup
            managers = set[int]()
            leaders = set[int]()
            async with db.execute(f"""SELECT p.id, tr.name FROM players p
                JOIN users u ON u.player_id = p.id
                JOIN user_team_roles ur ON ur.user_id = u.id
                JOIN team_roles tr ON tr.id = ur.role_id
                JOIN teams t ON t.id = ur.team_id
                JOIN team_rosters r ON r.team_id = t.id
                WHERE (tr.name = ? OR tr.name = ?)
                AND r.id IN (
                    SELECT tr.id {rosters_query}
                )""", (team_roles.MANAGER, team_roles.LEADER, *variable_parameters)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    player_id, role_name = row
                    if role_name == team_roles.MANAGER:
                        managers.add(player_id)
                    else:
                        leaders.add(player_id)

            fc_dict: dict[int, list[FriendCode]] = {}
            async with db.execute(f"""SELECT p.id, p.name, p.country_code, p.is_banned, 
                                  d.discord_id, d.username, d.discriminator, d.global_name, d.avatar,
                                  m.roster_id, m.join_date, m.is_bagger_clause
                                FROM players p
                                LEFT JOIN users u ON u.player_id = p.id
                                LEFT JOIN user_discords d ON u.id = d.user_id
                                JOIN team_members m ON p.id = m.player_id
                                WHERE m.leave_date IS NULL AND
                                m.roster_id IN (
                                  SELECT tr.id
                                  {rosters_query}
                                ) ORDER BY p.name COLLATE NOCASE""", variable_parameters) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    (player_id, name, country_code, is_banned, 
                     discord_id, d_username, d_discriminator, d_global_name, d_avatar,
                     roster_id, join_date, is_bagger_clause) = row
                    is_manager = player_id in managers
                    is_leader = player_id in leaders
                    player_discord = None
                    if discord_id:
                        player_discord = Discord(discord_id, d_username, d_discriminator, d_global_name, d_avatar)
                    if player_id not in fc_dict:
                        fc_dict[player_id] = []
                    player = RosterPlayerInfo(player_id, name, country_code, is_banned, player_discord, join_date, bool(is_manager), bool(is_leader), 
                                              bool(is_bagger_clause), fc_dict[player_id])
                    roster_dict[roster_id].append(player)
            
            fc_type = game_fc_map[self.game]
            async with db.execute(f"""SELECT DISTINCT f.id, f.player_id, f.type, f.fc, f.is_verified, f.is_primary, f.is_active, f.creation_date
                                  FROM friend_codes f
                                  JOIN players p ON f.player_id = p.id
                                  JOIN team_members m ON p.id = m.player_id
                                  WHERE f.type = ? AND m.leave_date IS NULL AND m.roster_id IN (
                                    SELECT tr.id
                                    {rosters_query}
                                  )""", (fc_type, *variable_parameters)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    fc_id, player_id, type, fc, is_verified, is_primary, is_active, creation_date = row
                    player_fcs = fc_dict.get(int(player_id), None)
                    if player_fcs is not None:
                        player_fcs.append(FriendCode(fc_id, fc, type, player_id, bool(is_verified), bool(is_primary), creation_date, is_active=bool(is_active)))
            return rosters

@save_to_command_log
@dataclass
class EditTeamMemberCommand(Command[None]):
    player_id: int
    roster_id: int
    team_id: int
    join_date: int | None
    leave_date: int | None
    is_bagger_clause: bool | None

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("""SELECT m.id, m.join_date, m.leave_date, m.is_bagger_clause FROM team_members m
                                    JOIN team_rosters r ON m.roster_id = r.id
                                    JOIN teams t ON r.team_id = t.id
                                    WHERE m.player_id = ? AND m.roster_id = ? AND t.id = ?
                                    ORDER BY m.join_date DESC
                                    """, (self.player_id, self.roster_id, self.team_id)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Team member not found", status=404)
                id, member_join_date, member_leave_date, member_is_bagger = row
                if not self.join_date:
                    self.join_date = member_join_date
                if self.is_bagger_clause is None:
                    self.is_bagger_clause = member_is_bagger
                # if we're kicking the member add log of it in team transfers
                if member_leave_date is None and self.leave_date is not None:
                    await db.execute("""INSERT INTO team_transfers(player_id, roster_id, date, roster_leave_id, is_accepted, approval_status, is_bagger_clause)
                                     VALUES(?, ?, ?, ?, ?, ?, ?)""", (self.player_id, None, self.leave_date, self.roster_id, True, "approved", member_is_bagger))
            await db.execute("UPDATE team_members SET join_date = ?, leave_date = ?, is_bagger_clause = ? WHERE id = ?", (self.join_date, self.leave_date, self.is_bagger_clause, id))
            await db.commit()