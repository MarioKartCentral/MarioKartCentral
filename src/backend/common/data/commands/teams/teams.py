from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from common.auth import team_roles
from common.data.command import Command
from common.data.db import DBWrapper
from common.data.models import *
from common.data.s3 import S3Wrapper, IMAGE_BUCKET
import base64

@dataclass
class CreateTeamCommand(Command[int | None]):
    name: str
    tag: str
    description: str
    language: str
    color: int
    logo_file: str | None
    approval_status: Approval
    is_historical: bool
    game: str
    mode: str
    is_recruiting: bool
    is_active: bool
    is_privileged: bool
    user_id: int | None = None

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        async with db_wrapper.connect() as db:
            name = self.name.strip()
            tag = self.tag.strip()
            valid_game_modes = {"mk8dx": ["150cc", "200cc"],
                                "mkw": ["rt", "ct"],
                                "mkt": ["vsrace"],
                                "mkworld": ["150cc"],}
            if self.game not in valid_game_modes:
                raise Problem(f"Invalid game (valid games: {', '.join(valid_game_modes.keys())})", status=400)
            if self.mode not in valid_game_modes[self.game]:
                raise Problem(f"Invalid mode (valid modes: {', '.join(valid_game_modes[self.game])})", status=400)
            if len(name) < 2:
                raise Problem("Team name must be at least 2 characters", status=400)
            if len(name) > 32:
                raise Problem("Team name must be 32 characters or less", status=400)
            if len(tag) < 1:
                raise Problem("Team tag must be at least 1 character", status=400)
            if len(tag) > 8:
                raise Problem("Team tag must be 8 characters or less", status=400)
            if len(self.description) > 500:
                raise Problem("Team description must be 500 characters or less", status=400)
            # we don't want users to be able to create teams that share the same name/tag as another team for this game, but it should be possible if moderators wish
            if not self.is_privileged:
                async with db.execute("""SELECT COUNT(r.id) 
                                      FROM team_rosters r
                                      JOIN teams t ON r.team_id = t.id
                                      WHERE ((r.name IS NOT NULL AND r.name = ?) OR (r.name IS NULL AND t.name = ?) 
                                      OR (r.tag IS NOT NULL AND r.tag = ?) OR (r.tag IS NULL AND t.tag = ?))
                                      AND r.game = ? AND r.mode = ? AND r.is_active = 1 AND t.is_historical = 0
                                      AND t.approval_status != 'denied' """, (name, name, tag, tag, self.game, self.mode)) as cursor:
                    row = await cursor.fetchone()
                    assert row is not None
                    if row[0] > 0:
                        raise Problem('An existing team for this game/mode already has this name or tag', status=400)
            if not self.is_privileged and self.user_id is not None:
                async with db.execute("""SELECT t.id FROM teams t
                                        JOIN user_team_roles ut ON t.id = ut.team_id
                                        WHERE t.approval_status = 'pending' AND ut.user_id = ?""", (self.user_id,)) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        raise Problem("You already have a pending team in the approval queue; you must wait for a staff member to approve/deny this team before creating another team", status=400)
            creation_date = int(datetime.now(timezone.utc).timestamp())
            async with db.execute("""INSERT INTO teams (name, tag, description, creation_date, language, color, logo, approval_status, is_historical)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", (name, tag, self.description, creation_date, self.language, self.color, None, self.approval_status,
                self.is_historical)) as cursor:
                team_id = cursor.lastrowid
            await db.execute("""INSERT INTO team_rosters(team_id, game, mode, name, tag, color, creation_date, is_recruiting, is_active, approval_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (team_id, self.game, self.mode, None, None, None, creation_date, self.is_recruiting, self.is_active, self.approval_status))
            logo_filename = f"team_logos/{team_id}.png"
            logo_path = f"/img/{logo_filename}"
            if self.logo_file:
                await db.execute("UPDATE teams SET logo = ? WHERE id = ?", (logo_path, team_id))
            # give the team creator manager permissions if their id was specified
            if self.user_id is not None:
                await db.execute("INSERT INTO user_team_roles(user_id, role_id, team_id) VALUES (?, 0, ?)", (self.user_id, team_id))
            if self.logo_file:
                logo_data = base64.b64decode(self.logo_file)
                await s3_wrapper.put_object(IMAGE_BUCKET, key=logo_filename, body=logo_data, acl="public-read")
            await db.commit()
            return team_id

@dataclass
class GetTeamInfoCommand(Command[Team]):
    team_id: int

    async def handle(self, db_wrapper: DBWrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT name, tag, description, creation_date, language, color, logo, approval_status, is_historical FROM teams WHERE id = ?",
                (self.team_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem('Team not found', status=404)
                team_name, team_tag, description, team_date, language, team_color, logo, team_approval_status, is_historical = row
                team = Team(self.team_id, team_name, team_tag, description, team_date, language, team_color, logo, team_approval_status, is_historical, [], [])

            # use a set for O(1) lookup
            managers = set[int]()
            leaders = set[int]()
            async with db.execute("""SELECT p.id, p.name, p.country_code, p.is_hidden, p.is_shadow, p.is_banned, p.join_date, tr.name FROM players p
                JOIN users u ON u.player_id = p.id
                JOIN user_team_roles ur ON ur.user_id = u.id
                JOIN team_roles tr ON tr.id = ur.role_id
                WHERE ur.team_id = ? AND (tr.name = ? OR tr.name = ?)""", (self.team_id, team_roles.MANAGER, team_roles.LEADER)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    player_id, name, country_code, is_hidden, is_shadow, is_banned, join_date, role_name = row
                    if role_name == team_roles.MANAGER:
                        team.managers.append(Player(player_id, name, country_code, is_hidden, is_shadow, is_banned, join_date, None))
                        managers.add(player_id)
                    else:
                        leaders.add(player_id)
            
            # get all rosters for our team
            rosters: list[TeamRoster] = []
            roster_dict: dict[int, TeamRoster] = {}
            async with db.execute("SELECT id, game, mode, name, tag, color, creation_date, is_recruiting, is_active, approval_status FROM team_rosters WHERE team_id = ?",
                (self.team_id,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    roster_id, game, mode, roster_name, roster_tag, roster_color, roster_date, is_recruiting, is_active, roster_approval_status = row
                    if roster_name is None:
                        roster_name = team_name
                    if roster_tag is None:
                        roster_tag = team_tag
                    if roster_color is None:
                        roster_color = team_color
                    curr_roster = TeamRoster(roster_id, self.team_id, game, mode, roster_name, roster_tag, roster_date, is_recruiting, is_active, roster_approval_status, roster_color, [], [])
                    rosters.append(curr_roster)
                    roster_dict[curr_roster.id] = curr_roster
            
            team_members: list[PartialTeamMember] = []
            # get all current team members who are in a roster that belongs to our team
            roster_id_query = ','.join(map(str, roster_dict.keys()))
            async with db.execute(f"""SELECT m.player_id, m.roster_id, m.join_date, m.is_bagger_clause
                                    FROM team_members m
                                    JOIN players p ON m.player_id = p.id
                                    WHERE roster_id IN ({roster_id_query}) AND leave_date IS ?
                                    ORDER BY p.name COLLATE NOCASE
                                    """, (None,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    player_id, roster_id, join_date, is_bagger_clause = row
                    curr_team_member = PartialTeamMember(player_id, roster_id, join_date, bool(is_bagger_clause))
                    team_members.append(curr_team_member)

            team_invites: list[PartialTeamMember] = []
            # get all invited players to a roster on our team
            async with db.execute(f"""SELECT t.player_id, t.roster_id, t.date, t.is_bagger_clause
                                  FROM team_transfers t
                                  JOIN players p ON t.player_id = p.id
                                  WHERE roster_id IN ({roster_id_query}) AND approval_status = 'pending'
                                  ORDER BY p.name COLLATE NOCASE""") as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    player_id, roster_id, join_date, is_bagger_clause = row
                    curr_invited_player = PartialTeamMember(player_id, roster_id, join_date, bool(is_bagger_clause))
                    team_invites.append(curr_invited_player)

            player_dict: dict[int, PartialPlayer] = {}

            if len(team_members) > 0 or len(team_invites) > 0:
                # get info about all players who are in/invited to at least 1 roster on our team
                member_id_query = ','.join(set([str(m.player_id) for m in team_members] + [str(m.player_id) for m in team_invites]))
                async with db.execute(f"""SELECT p.id, p.name, p.country_code, p.is_banned, 
                                      d.discord_id, d.username, d.discriminator, d.global_name, d.avatar 
                                      FROM players p
                                      LEFT JOIN users u ON u.player_id = p.id
                                      LEFT JOIN user_discords d ON u.id = d.user_id
                                      WHERE p.id IN ({member_id_query})""") as cursor:
                    rows = await cursor.fetchall()
                    for row in rows:
                        (player_id, player_name, country, is_banned, 
                         discord_id, d_username, d_discriminator, d_global_name, d_avatar) = row
                        player_discord = None
                        if discord_id:
                            player_discord = Discord(discord_id, d_username, d_discriminator, d_global_name, d_avatar)
                        player_dict[player_id] = PartialPlayer(player_id, player_name, country, bool(is_banned), player_discord, [])

                # get all friend codes for members of our team that are from a game that our team has a roster for
                fc_type_query = ','.join(set([f"'{game_fc_map[r.game]}'" for r in rosters]))
                async with db.execute(f"SELECT id, player_id, type, fc, is_verified, is_primary, is_active, creation_date FROM friend_codes WHERE player_id IN ({member_id_query}) AND type IN ({fc_type_query})") as cursor:
                    rows = await cursor.fetchall()
                    for row in rows:
                        id, player_id, type, fc, is_verified, is_primary, is_active, creation_date = row
                        curr_fc = FriendCode(id, fc, type, player_id, bool(is_verified), bool(is_primary), creation_date, is_active=bool(is_active))
                        player_dict[player_id].friend_codes.append(curr_fc)

            for member in team_members:
                curr_roster = roster_dict[member.roster_id]
                p = player_dict[member.player_id]
                is_manager = p.player_id in managers
                is_leader = p.player_id in leaders
                curr_player = RosterPlayerInfo(p.player_id, p.name, p.country_code, p.is_banned, p.discord, member.join_date, is_manager, is_leader, member.is_bagger_clause,
                    [fc for fc in p.friend_codes if fc.type == game_fc_map[curr_roster.game]]) # only add FCs that are for the same game as current roster
                curr_roster.players.append(curr_player)

            for invite in team_invites:
                curr_roster = roster_dict[invite.roster_id]
                p = player_dict[invite.player_id]
                curr_player = RosterInvitedPlayer(p.player_id, p.name, p.country_code, p.is_banned, p.discord, invite.join_date, invite.is_bagger_clause,
                    [fc for fc in p.friend_codes if fc.type == game_fc_map[curr_roster.game]]) # only add FCs that are for the same game as current roster
                curr_roster.invites.append(curr_player) 

            team.rosters = rosters
            return team

@dataclass
class EditTeamCommand(Command[None]):
    team_id: int
    name: str
    tag: str
    description: str
    language: str
    color: int
    logo_file: str | None
    remove_logo: bool
    approval_status: Approval
    is_historical: bool
    is_privileged: bool
    mod_player_id: int | None

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        if len(self.name) > 32:
            raise Problem("Team name must be 32 characters or less", status=400)
        if len(self.tag) > 8:
            raise Problem("Team tag must be 8 characters or less", status=400)
        if len(self.description) > 500:
            raise Problem("Team description must be 500 characters or less", status=400)
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT name, tag, logo FROM teams WHERE id = ?", (self.team_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Team not found", status=404)
                team_name, team_tag, logo_path = row
            if self.logo_file:
                logo_path = f"/img/team_logos/{self.team_id}.png"
            elif self.remove_logo:
                logo_path = None
            await db.execute("""UPDATE teams SET name = ?,
                tag = ?,
                description = ?,
                language = ?,
                color = ?,
                logo = ?,
                approval_status = ?,
                is_historical = ?
                WHERE id = ?""",
                (self.name.strip(), self.tag.strip(), self.description, self.language, self.color, logo_path, self.approval_status, self.is_historical, self.team_id))
            # add a team name/tag change log if we're changing one of those values
            if team_name != self.name or team_tag != self.tag:
                now = int(datetime.now(timezone.utc).timestamp())
                await db.execute("""INSERT INTO team_edits(team_id, old_name, new_name, old_tag, new_tag, date, approval_status, handled_by)
                                    VALUES(?, ?, ?, ?, ?, ?, ?, ?)""", (self.team_id, team_name, self.name.strip(), team_tag.strip(), self.tag, now, "approved", self.mod_player_id))
            # if team is approved, approve all rosters that are pending; if team is not approved, change all approved rosters to pending
            if self.approval_status == "approved":
                await db.execute("UPDATE team_rosters SET approval_status = 'approved' WHERE team_id = ? AND approval_status = 'pending'", (self.team_id,))
            else:
                await db.execute("UPDATE team_rosters SET approval_status = 'pending' WHERE team_id = ? AND approval_status = 'approved'", (self.team_id,))
            if self.logo_file:
                logo_filename = f"team_logos/{self.team_id}.png"
                logo_data = base64.b64decode(self.logo_file)
                await s3_wrapper.put_object(IMAGE_BUCKET, key=logo_filename, body=logo_data, acl="public-read")
            elif self.remove_logo:
                logo_filename = f"team_logos/{self.team_id}.png"
                await s3_wrapper.delete_object(IMAGE_BUCKET, key=logo_filename)
            await db.commit()

@dataclass
class ApproveDenyTeamCommand(Command[None]):
    team_id: int
    approval_status: Approval

    async def handle(self, db_wrapper: DBWrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("UPDATE teams SET approval_status = ? WHERE id = ?", (self.approval_status, self.team_id)) as cursor:
                updated_rows = cursor.rowcount
                if updated_rows == 0:
                    raise Problem("No team found", status=404)
            if self.approval_status == 'approved':
                await db.execute("UPDATE team_rosters SET approval_status = ? WHERE team_id = ? AND approval_status = 'pending'", (self.approval_status, self.team_id))
            await db.commit()

@dataclass
class ManagerEditTeamCommand(Command[None]):
    team_id: int
    description: str
    language: str
    color: int
    logo_file: str | None
    remove_logo: bool

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        if len(self.description) > 500:
            raise Problem("Team description must be 500 characters or less", status=400)
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT logo FROM teams WHERE id = ?", (self.team_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Team not found", status=404)
                logo_path = row[0]
            if self.logo_file:
                logo_path = f"/img/team_logos/{self.team_id}.png"
            elif self.remove_logo:
                logo_path = None
            async with db.execute("""UPDATE teams SET
                description = ?,
                language = ?,
                color = ?,
                logo = ?
                WHERE id = ?""",
                (self.description, self.language, self.color, logo_path, self.team_id)) as cursor:
                updated_rows = cursor.rowcount
                if updated_rows == 0:
                    raise Problem('No team found', status=404)
            if self.logo_file:
                logo_filename = f"team_logos/{self.team_id}.png"
                logo_data = base64.b64decode(self.logo_file)
                await s3_wrapper.put_object(IMAGE_BUCKET, key=logo_filename, body=logo_data, acl="public-read")
            elif self.remove_logo:
                logo_filename = f"team_logos/{self.team_id}.png"
                await s3_wrapper.delete_object(IMAGE_BUCKET, key=logo_filename)
            await db.commit()

@dataclass
class RequestEditTeamCommand(Command[None]):
    team_id: int
    name: str
    tag: str

    async def handle(self, db_wrapper: DBWrapper):
        if len(self.name) > 32:
            raise Problem("Team name must be 32 characters or less", status=400)
        if len(self.tag) > 8:
            raise Problem("Team tag must be 8 characters or less", status=400)
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT name, tag, approval_status FROM teams WHERE id = ?", (self.team_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Team not found")
                name, tag, approval_status = row
                if self.name == name and self.tag == tag:
                    raise Problem("At least one of the team name or tag must be different from their current values", status=400)
                if approval_status != "approved":
                    raise Problem("Cannot request to edit team if it is not approved", status=400)
            # check if this team has made a request in the last 90 days
            async with db.execute("SELECT date FROM team_edits WHERE team_id = ? AND date > ? AND approval_status != 'denied' LIMIT 1",
                                  (self.team_id, (datetime.now(timezone.utc)-timedelta(minutes=90)).timestamp())) as cursor:
                row = await cursor.fetchone()
                if row:
                    raise Problem("Roster has requested name/tag change in the last 90 days", status=400)
            creation_date = int(datetime.now(timezone.utc).timestamp())
            await db.execute("INSERT INTO team_edits(team_id, old_name, new_name, old_tag, new_tag, date, approval_status) VALUES(?, ?, ?, ?, ?, ?, ?)",
                            (self.team_id, name, self.name, tag, self.tag, creation_date, "pending"))
            await db.commit()

@dataclass
class ViewTeamEditHistoryCommand(Command[list[TeamEdit]]):
    team_id: int

    async def handle(self, db_wrapper: DBWrapper):
        edits: list[TeamEdit] = []
        async with db_wrapper.connect() as db:
            async with db.execute("""SELECT r.id, r.team_id, r.old_name, r.new_name, r.old_tag, r.new_tag, r.date, r.approval_status, r.handled_by, p.name, p.country_code, p.is_banned, t.color
                                    FROM team_edits r
                                    JOIN teams t ON r.team_id = t.id
                                    LEFT JOIN players p ON r.handled_by = p.id
                                    WHERE r.team_id = ? AND r.approval_status != ?""",
                                    (self.team_id, "denied")) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    (request_id, team_id, old_name, new_name, old_tag, new_tag, date, approval_status, 
                     handled_by_id, handled_by_name, handled_by_country, handled_by_banned, color) = row
                    handled_by = None
                    if handled_by_id:
                        handled_by = PlayerBasic(handled_by_id, handled_by_name, handled_by_country, bool(handled_by_banned))
                    edits.append(TeamEdit(request_id, team_id, old_name, old_tag, new_name, new_tag, color, date, approval_status, handled_by))
        return edits

@dataclass
class ApproveTeamEditCommand(Command[None]):
    request_id: int
    mod_player_id: int | None

    async def handle(self, db_wrapper: DBWrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT team_id, new_name, new_tag FROM team_edits WHERE id = ?", (self.request_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem("Team edit request not found", status=404)
                team_id, name, tag = row
            await db.execute("UPDATE teams SET name = ?, tag = ? WHERE id = ?", (name, tag, team_id))
            await db.execute("UPDATE team_edits SET approval_status = 'approved', handled_by = ? WHERE id = ?", (self.mod_player_id, self.request_id))
            await db.commit()

@dataclass
class DenyTeamEditCommand(Command[None]):
    request_id: int
    mod_player_id: int

    async def handle(self, db_wrapper: DBWrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("UPDATE team_edits SET approval_status = 'denied', handled_by = ? WHERE id = ?", (self.mod_player_id, self.request_id)) as cursor:
                rowcount = cursor.rowcount
                if rowcount == 0:
                    raise Problem("Team edit request not found", status=404)
            await db.commit()

@dataclass
class ListTeamEditRequestsCommand(Command[TeamEditList]):
    filter: TeamEditFilter

    async def handle(self, db_wrapper: DBWrapper):
        requests: list[TeamEdit] = []
        filter = self.filter
        limit = 20
        offset = 0
        if filter.page is not None:
            offset = (filter.page - 1) * limit

        request_query = """FROM team_edits r
                            JOIN teams t ON r.team_id = t.id
                            LEFT JOIN players p ON r.handled_by = p.id
                            WHERE r.approval_status = ?"""
        
        async with db_wrapper.connect() as db:
            async with db.execute(f"""SELECT r.id, r.team_id, r.old_name, r.new_name, r.old_tag, r.new_tag, r.date, r.approval_status, r.handled_by, p.name, p.country_code, p.is_banned, t.color
                                    {request_query} ORDER BY r.date DESC LIMIT ? OFFSET ?""", (filter.approval_status, limit, offset)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    (request_id, team_id, old_name, new_name, old_tag, new_tag, date, approval_status, 
                     handled_by_id, handled_by_name, handled_by_country, handled_by_banned, color) = row
                    handled_by = None
                    if handled_by_id:
                        handled_by = PlayerBasic(handled_by_id, handled_by_name, handled_by_country, bool(handled_by_banned))
                    requests.append(TeamEdit(request_id, team_id, old_name, old_tag, new_name, new_tag, color, date, approval_status, handled_by))

            count_query = f"SELECT COUNT(*) {request_query}"
            async with db.execute(count_query, (filter.approval_status,)) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                request_count = row[0]

            page_count = int(request_count / limit) + (1 if request_count % limit else 0)

        return TeamEditList(requests, request_count, page_count)


@dataclass
class ListTeamsCommand(Command[TeamList]):
    team_filter: TeamFilter
    approval_status: Approval | None = "approved"

    async def handle(self, db_wrapper: DBWrapper):
        team_filter = self.team_filter
        async with db_wrapper.connect() as db:

            limit: int = 50
            offset: int = 0
            
            order_by = 't.creation_date' if team_filter.sort_by_newest else 't.name'
            desc = 'DESC' if team_filter.sort_by_newest else ''

            filter_query: dict[str, list[Any]] = {
                "where_clauses": [],
                "variable_parameters": []
            }

            if team_filter.page is not None:
                offset = (team_filter.page - 1) * limit

            def append_equal_filter(filter_query: dict[str, list[str]], filter_value: Any, column_name: str) -> None:
                if filter_value is not None:
                    filter_query["where_clauses"].append(f"{column_name} = ?")
                    filter_query["variable_parameters"].append(filter_value)

            # check both the team and team_roster fields with the same name for a match
            def append_team_roster_like_filter(filter_query: dict[str, list[str]], filter_value: Any, column_name: str) -> None:
                if filter_value is not None:
                    filter_query["where_clauses"].append(f"(t.{column_name} LIKE ? OR r.{column_name} LIKE ?)")
                    filter_query["variable_parameters"].extend([f"%{filter_value}%", f"%{filter_value}%"])

            if team_filter.name_or_tag is not None:
                filter_query["where_clauses"].append("(t.name LIKE ? OR t.tag LIKE ? OR r.name LIKE ? OR r.tag LIKE ?)")
                filter_query["variable_parameters"].extend([f"%{team_filter.name_or_tag}%"]*4)

            append_team_roster_like_filter(filter_query, team_filter.name, "name")
            append_team_roster_like_filter(filter_query, team_filter.tag, "tag")
            append_equal_filter(filter_query, team_filter.language, "t.language")
            append_equal_filter(filter_query, team_filter.is_historical, "t.is_historical")
            append_equal_filter(filter_query, self.approval_status, "t.approval_status")
            append_equal_filter(filter_query, team_filter.game, "r.game")
            append_equal_filter(filter_query, team_filter.mode, "r.mode")
            append_equal_filter(filter_query, team_filter.is_recruiting, "r.is_recruiting")
            append_equal_filter(filter_query, team_filter.is_active, "r.is_active")
            append_equal_filter(filter_query, self.approval_status, "r.approval_status")

            team_select = """
                SELECT DISTINCT t.id, t.name, t.tag, t.description,
                t.creation_date, t.language, t.color, t.logo,
                t.approval_status, t.is_historical
                FROM teams t
                JOIN team_rosters r ON t.id = r.team_id
            """
            where_clause = "" if not filter_query["where_clauses"] else f"WHERE {' AND '.join(filter_query["where_clauses"])}"
            having_clause = ""

            # Join team_members table only if querying active members
            if team_filter.min_player_count:
                filter_query["variable_parameters"].append(team_filter.min_player_count)
                team_select +=  " LEFT JOIN team_members m on r.id = m.roster_id"
                having_clause = "GROUP BY r.id HAVING COUNT(m.roster_id) >= ?"

            team_query = " ".join([
                team_select,
                where_clause,
                having_clause,
                f"ORDER BY {order_by} COLLATE NOCASE {desc}",
                "LIMIT ? OFFSET ?"
            ])

            teams: dict[int, Team] = {}
            async with db.execute(team_query, (*filter_query["variable_parameters"], limit, offset)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    (tid, tname, ttag, description, tdate, lang, color, logo, tapprove, is_historical) = row
                    team = Team(tid, tname, ttag, description, tdate, lang, color, logo, tapprove, bool(is_historical), [], [])
                    teams[tid] = team

            team_ids, team_list = teams.keys(), teams.values()
            rosters_query = f"""SELECT r.id, r.team_id, r.game, r.mode, r.name, r.tag, r.color, r.creation_date, r.is_recruiting,
                                        r.is_active, r.approval_status
                                        FROM team_rosters r
                                        WHERE r.team_id IN ({", ".join([str(tid) for tid in team_ids])}) LIMIT ? OFFSET ?
                                        """
            async with db.execute(rosters_query, (limit, offset)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    roster_id, team_id, game, mode, name, tag, roster_color, creation_date, is_recruiting, is_active, approval_status = row
                    team = teams[team_id]
                    roster = TeamRoster(roster_id, team_id, game, mode, name if name else team.name, tag if tag else team.tag, creation_date,
                                        bool(is_recruiting), bool(is_active), approval_status, roster_color if roster_color else team.color, [], [])
                    team.rosters.append(roster)

            team_count: int = len(team_list)
            page_count: int = int(team_count / limit) + (1 if team_count % limit else 0)
  
            return TeamList(list(team_list), team_count, page_count)
    

@dataclass
class MergeTeamsCommand(Command[None]):
    from_team_id: int
    to_team_id: int

    async def handle(self, db_wrapper: DBWrapper):
        if self.from_team_id == self.to_team_id:
            raise Problem("Team IDs are equal", status=400)
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT name, tag, color FROM teams WHERE id = ?", (self.from_team_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem(f"Team ID {self.from_team_id} not found", status=404)
                old_name, old_tag, old_color = row
            async with db.execute("SELECT id FROM teams WHERE id = ?", (self.to_team_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem(f"Team ID {self.to_team_id} not found", status=404)
            # don't want to change the name/tag of a roster to the new team's name if it's the default value
            await db.execute("UPDATE team_rosters SET name = ? WHERE team_id = ? AND name IS NULL", (old_name, self.from_team_id))
            await db.execute("UPDATE team_rosters SET tag = ? WHERE team_id = ? AND tag IS NULL", (old_tag, self.from_team_id))
            await db.execute("UPDATE team_rosters SET color = ? WHERE team_id = ? AND color IS NULL", (old_color, self.from_team_id))

            await db.execute("UPDATE team_rosters SET team_id = ? WHERE team_id = ?", (self.to_team_id, self.from_team_id))
            await db.execute("DELETE FROM user_team_roles WHERE team_id = ?", (self.from_team_id,))
            await db.execute("DELETE FROM team_edits WHERE team_id = ?", (self.from_team_id,))
            await db.execute("DELETE FROM teams WHERE id = ?", (self.from_team_id,))
            await db.commit()