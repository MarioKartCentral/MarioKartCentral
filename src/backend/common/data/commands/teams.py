from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import List

from common.data.commands import Command, save_to_command_log
from common.data.models import *
from common.auth import team_permissions, team_roles


@save_to_command_log
@dataclass
class CreateTeamCommand(Command[int | None]):
    name: str
    tag: str
    description: str
    language: str
    color: int
    logo: str | None
    approval_status: Approval
    is_historical: bool
    game: str
    mode: str
    is_recruiting: bool
    is_active: bool
    is_privileged: bool
    user_id: int | None = None

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            valid_game_modes = {"mk8dx": ["150cc", "200cc"],
                                "mkw": ["rt", "ct"],
                                "mkt": ["vsrace"]}
            if self.game not in valid_game_modes:
                raise Problem(f"Invalid game (valid games: {', '.join(valid_game_modes.keys())})", status=400)
            if self.mode not in valid_game_modes[self.game]:
                raise Problem(f"Invalid mode (valid modes: {', '.join(valid_game_modes[self.game])})", status=400)
            # we don't want users to be able to create teams that share the same name/tag as another team, but it should be possible if moderators wish
            if not self.is_privileged:
                async with db.execute("SELECT COUNT(id) FROM team_rosters WHERE name = ? OR tag = ? AND is_active = 0", (self.name, self.tag)) as cursor:
                    row = await cursor.fetchone()
                    assert row is not None
                    if row[0] > 0:
                        raise Problem('An existing team already has this name or tag', status=400)
            creation_date = int(datetime.now(timezone.utc).timestamp())
            async with db.execute("""INSERT INTO teams (name, tag, description, creation_date, language, color, logo, approval_status, is_historical)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", (self.name, self.tag, self.description, creation_date, self.language, self.color, self.logo, self.approval_status,
                self.is_historical)) as cursor:
                team_id = cursor.lastrowid
            await db.execute("""INSERT INTO team_rosters(team_id, game, mode, name, tag, creation_date, is_recruiting, is_active, approval_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", (team_id, self.game, self.mode, None, None, creation_date, self.is_recruiting, self.is_active, self.approval_status))
            # give the team creator manager permissions if their id was specified
            if self.user_id is not None:
                await db.execute("INSERT INTO user_team_roles(user_id, role_id, team_id) VALUES (?, 0, ?)", (self.user_id, team_id))
            await db.commit()
            return team_id

@dataclass
class GetTeamInfoCommand(Command[Team]):
    team_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT name, tag, description, creation_date, language, color, logo, approval_status, is_historical FROM teams WHERE id = ?",
                (self.team_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem('Team not found', status=404)
                team_name, team_tag, description, team_date, language, color, logo, team_approval_status, is_historical = row
                team = Team(self.team_id, team_name, team_tag, description, team_date, language, color, logo, team_approval_status, is_historical, [], [])

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
            async with db.execute("SELECT id, game, mode, name, tag, creation_date, is_recruiting, is_active, approval_status FROM team_rosters WHERE team_id = ?",
                (self.team_id,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    roster_id, game, mode, roster_name, roster_tag, roster_date, is_recruiting, is_active, roster_approval_status = row
                    if roster_name is None:
                        roster_name = team_name
                    if roster_tag is None:
                        roster_tag = team_tag
                    curr_roster = TeamRoster(roster_id, self.team_id, game, mode, roster_name, roster_tag, roster_date, is_recruiting, is_active, roster_approval_status, color, [], [])
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
                game_query = ','.join(set([f"'{r.game}'" for r in rosters]))
                async with db.execute(f"SELECT id, player_id, game, fc, is_verified, is_primary, is_active FROM friend_codes WHERE player_id IN ({member_id_query}) AND game IN ({game_query})") as cursor:
                    rows = await cursor.fetchall()
                    for row in rows:
                        id, player_id, game, fc, is_verified, is_primary, is_active = row
                        curr_fc = FriendCode(id, fc, game, player_id, bool(is_verified), bool(is_primary), is_active=bool(is_active))
                        player_dict[player_id].friend_codes.append(curr_fc)

            for member in team_members:
                curr_roster = roster_dict[member.roster_id]
                p = player_dict[member.player_id]
                is_manager = p.player_id in managers
                is_leader = p.player_id in leaders
                curr_player = RosterPlayerInfo(p.player_id, p.name, p.country_code, p.is_banned, p.discord, member.join_date, is_manager, is_leader, member.is_bagger_clause,
                    [fc for fc in p.friend_codes if fc.game == curr_roster.game]) # only add FCs that are for the same game as current roster
                curr_roster.players.append(curr_player)

            for invite in team_invites:
                curr_roster = roster_dict[invite.roster_id]
                p = player_dict[invite.player_id]
                curr_player = RosterInvitedPlayer(p.player_id, p.name, p.country_code, p.is_banned, p.discord, invite.join_date, invite.is_bagger_clause,
                    [fc for fc in p.friend_codes if fc.game == curr_roster.game]) # only add FCs that are for the same game as current roster
                curr_roster.invites.append(curr_player) 

            team.rosters = rosters
            return team

@save_to_command_log
@dataclass
class EditTeamCommand(Command[None]):
    team_id: int
    name: str
    tag: str
    description: str
    language: str
    color: int
    logo: str | None
    approval_status: Approval
    is_historical: bool
    is_privileged: bool

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("""UPDATE teams SET name = ?,
                tag = ?,
                description = ?,
                language = ?,
                color = ?,
                logo = ?,
                approval_status = ?,
                is_historical = ?
                WHERE id = ?""",
                (self.name, self.tag, self.description, self.language, self.color, self.logo, self.approval_status, self.is_historical, self.team_id)) as cursor:
                updated_rows = cursor.rowcount
                if updated_rows == 0:
                    raise Problem('No team found', status=404)
            # if team is approved, approve all rosters that are pending; if team is not approved, change all approved rosters to pending
            if self.approval_status == "approved":
                await db.execute("UPDATE team_rosters SET approval_status = 'approved' WHERE team_id = ? AND approval_status = 'pending'", (self.team_id,))
            else:
                await db.execute("UPDATE team_rosters SET approval_status = 'pending' WHERE team_id = ? AND approval_status = 'approved'", (self.team_id,))
            await db.commit()

@save_to_command_log
@dataclass
class ApproveDenyTeamCommand(Command[None]):
    team_id: int
    approval_status: Approval

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("UPDATE teams SET approval_status = ? WHERE id = ?", (self.approval_status, self.team_id)) as cursor:
                updated_rows = cursor.rowcount
                if updated_rows == 0:
                    raise Problem("No team found", status=404)
            if self.approval_status == 'approved':
                await db.execute("UPDATE team_rosters SET approval_status = ? WHERE team_id = ? AND approval_status = 'pending'", (self.approval_status, self.team_id))
            await db.commit()

@save_to_command_log
@dataclass
class ManagerEditTeamCommand(Command[None]):
    team_id: int
    description: str
    language: str
    color: int
    logo: str | None

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("""UPDATE teams SET
                description = ?,
                language = ?,
                color = ?,
                logo = ?
                WHERE id = ?""",
                (self.description, self.language, self.color, self.logo, self.team_id)) as cursor:
                updated_rows = cursor.rowcount
                if updated_rows == 0:
                    raise Problem('No team found', status=404)
                await db.commit()

@save_to_command_log
@dataclass
class RequestEditTeamCommand(Command[None]):
    team_id: int
    name: str
    tag: str

    async def handle(self, db_wrapper, s3_wrapper):
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
            async with db.execute("SELECT date FROM team_edit_requests WHERE team_id = ? AND date > ? AND approval_status != 'denied' LIMIT 1",
                                  (self.team_id, (datetime.now(timezone.utc)-timedelta(minutes=90)).timestamp())) as cursor:
                row = await cursor.fetchone()
                if row:
                    raise Problem("Roster has requested name/tag change in the last 90 days", status=400)
            creation_date = int(datetime.now(timezone.utc).timestamp())
            await db.execute("INSERT INTO team_edit_requests(team_id, name, tag, date, approval_status) VALUES(?, ?, ?, ?, ?)",
                            (self.team_id, self.name, self.tag, creation_date, "pending"))
            await db.commit()

@dataclass
class ViewTeamEditHistoryCommand(Command[list[TeamEditRequest]]):
    team_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        edits: list[TeamEditRequest] = []
        async with db_wrapper.connect() as db:
            async with db.execute("""SELECT r.id, r.team_id, r.name, r.tag, r.date, r.approval_status, t.name, t.tag, t.color
                                    FROM team_edit_requests r JOIN teams t ON r.team_id = t.id WHERE r.team_id = ? AND r.approval_status != ?""",
                                    (self.team_id, "denied")) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    request_id, team_id, new_name, new_tag, date, approval_status, old_name, old_tag, color = row
                    edits.append(TeamEditRequest(request_id, team_id, old_name, old_tag, new_name, new_tag, color, date, approval_status))
        return edits

@dataclass
class ViewRosterEditHistoryCommand(Command[list[RosterEditRequest]]):
    team_id: int
    roster_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        edits: list[RosterEditRequest] = []
        async with db_wrapper.connect() as db:
            async with db.execute("""SELECT re.id, re.roster_id, re.name, re.tag, re.date, re.approval_status, r.name, r.tag,
                                  t.color, t.id, t.name, t.tag FROM roster_edit_requests re JOIN team_rosters r ON re.roster_id = r.id
                                  JOIN teams t ON r.team_id = t.id
                                  WHERE re.roster_id = ? AND re.approval_status != ?""",
                                  (self.roster_id, "denied")) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    request_id, roster_id, new_name, new_tag, date, approval_status, old_name, old_tag, color, team_id, team_name, team_tag = row
                    edits.append(RosterEditRequest(request_id, roster_id, team_id, team_name, team_tag, old_name, old_tag, new_name, new_tag, color, date, approval_status))
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
        async with db_wrapper.connect() as db:
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
    name: str | None
    tag: str | None
    is_recruiting: bool
    is_active: bool
    approval_status: Approval

    async def handle(self, db_wrapper, s3_wrapper):
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
            if self.name == team_name:
                self.name = None
            if self.tag == team_tag:
                self.tag = None
            # get the current roster's name and check if it exists
            async with db.execute("SELECT name, game, mode FROM team_rosters WHERE id = ? AND team_id = ?", (self.roster_id, self.team_id)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem('No roster found')
                roster_name, game, mode = row
            if roster_name != self.name:
                # check to make sure another roster doesn't have the name we're changing to
                async with db.execute("SELECT name FROM team_rosters WHERE team_id = ? AND game = ? AND mode = ? AND name IS ? AND id != ?", (self.team_id, game, mode, self.name, self.roster_id)) as cursor:
                    row = await cursor.fetchone()
                    if row is not None:
                        raise Problem('Only one roster per game/mode may use the same name', status=400)
            await db.execute("""UPDATE team_rosters SET team_id = ?, name = ?, tag = ?, is_recruiting = ?, is_active = ?, approval_status = ?
                                WHERE id = ?""",
                             (self.team_id, self.name, self.tag, self.is_recruiting, self.is_active, self.approval_status, self.roster_id))
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
class InvitePlayerCommand(Command[None]):
    player_id: int
    roster_id: int
    team_id: int
    is_bagger_clause: bool

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT team_id, game, approval_status FROM team_rosters WHERE id = ?", (self.roster_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Roster not found", status=404)
                roster_team_id, game, approval_status = row
                if approval_status != "approved":
                    raise Problem("Cannot invite players to roster if it is not approved", status=400)
                if int(roster_team_id) != self.team_id:
                    raise Problem("Roster is not part of specified team", status=400)
                if self.is_bagger_clause and game != "mkw":
                    raise Problem("Cannot invite players as baggers for games other than MKW", status=400)
            async with db.execute("SELECT id FROM players WHERE id = ?", (self.player_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Player not found", status=404)
            async with db.execute("SELECT id FROM friend_codes WHERE game = ? AND player_id = ? AND is_active = ?", (game, self.player_id, True)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Player has no friend codes for this game", status=400)
            async with db.execute("SELECT id FROM team_members WHERE player_id = ? AND roster_id = ? AND leave_date IS ?", (self.player_id, self.roster_id, None)) as cursor:
                row = await cursor.fetchone()
                if row:
                    raise Problem("Player is already on this roster", status=400)
            async with db.execute("SELECT COUNT(id) FROM team_transfers WHERE player_id = ? AND roster_id = ? AND approval_status != 'approved'", (self.player_id, self.roster_id)) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                num_invites = row[0]
                if num_invites > 0:
                    raise Problem("Player has already been invited", status=400)
            creation_date = int(datetime.now(timezone.utc).timestamp())
            await db.execute("INSERT INTO team_transfers(player_id, roster_id, date, is_bagger_clause, is_accepted, approval_status) VALUES (?, ?, ?, ?, ?, ?)", 
                             (self.player_id, self.roster_id, creation_date, self.is_bagger_clause, False, "pending"))
            await db.commit()

@save_to_command_log
@dataclass
class DeleteInviteCommand(Command[None]):
    player_id: int
    roster_id: int
    team_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT team_id FROM team_rosters WHERE id = ?", (self.roster_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Roster not found", status=404)
                roster_team_id = row[0]
                if int(roster_team_id) != self.team_id:
                    raise Problem("Roster is not part of specified team", status=400)
            async with db.execute("DELETE FROM team_transfers WHERE player_id = ? AND roster_id = ?", (self.player_id, self.roster_id)) as cursor:
                rowcount = cursor.rowcount
                if rowcount == 0:
                    raise Problem("Invite not found", status=404)
            await db.commit()

@save_to_command_log
@dataclass
class AcceptInviteCommand(Command[None]):
    invite_id: int
    roster_leave_id: int | None
    player_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            # check if invite exists and to make sure we're the same player as the invite
            async with db.execute("SELECT r.game, i.player_id FROM team_transfers i JOIN team_rosters r ON i.roster_id = r.id WHERE i.id = ?", (self.invite_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem("No invite found", status=404)
                game, invite_player_id = row
                if self.player_id != invite_player_id:
                    raise Problem("Cannot accept invite for another player", status=400)
            # make sure that we are actually in the roster we're leaving
            if self.roster_leave_id:
                async with db.execute("SELECT id FROM team_members WHERE roster_id = ? AND player_id = ? AND leave_date IS ?", (self.roster_leave_id, self.player_id, None)) as cursor:
                    row = await cursor.fetchone()
                    if row is None:
                        raise Problem("Player is not registered for the roster they are leaving", status=400)
            # make sure we have at least one FC for the game of the roster that we are accepting an invite for
            async with db.execute("SELECT count(id) FROM friend_codes WHERE player_id = ? AND game = ?", (self.player_id, game)) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                fc_count = row[0]
                if fc_count == 0:
                    raise Problem("Player does not have any friend codes for this roster's game", status=400)
            # we do not move the player to the team's roster just yet, just mark it as accepted, a moderator must approve the transfer
            await db.execute("UPDATE team_transfers SET roster_leave_id = ?, is_accepted = ? WHERE id = ?", (self.roster_leave_id, True, self.invite_id))
            await db.commit()

@save_to_command_log
@dataclass
class DeclineInviteCommand(Command[None]):
    invite_id: int
    player_id: int
    is_privileged: bool = False

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            # check if invite exists and to make sure we're the same player as the invite
            async with db.execute("SELECT player_id FROM team_transfers WHERE id = ?", (self.invite_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem("No invite found", status=404)
                invite_player_id = row[0]
                if self.player_id != invite_player_id and not self.is_privileged:
                    raise Problem("Cannot decline invite for another player", status=400)
            await db.execute("DELETE FROM team_transfers WHERE id = ?", (self.invite_id,))
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
            async with db.execute("""SELECT p.squad_id FROM tournament_players p
                                JOIN team_squad_registrations s ON p.squad_id = s.squad_id
                                JOIN tournaments t ON p.tournament_id = t.id
                                WHERE p.player_id = ? AND s.roster_id = ?
                                AND (t.date_end > ? OR t.registrations_open = ?) AND t.team_members_only = ?""",
                                (self.player_id, self.roster_id, leave_date, True, True)) as cursor:
                rows = await cursor.fetchall()
                squad_ids: list[int] = [row[0] for row in rows]
            # finally remove the player from all the tournaments they shouldn't be in
            await db.execute(f"DELETE FROM tournament_players WHERE player_id = ? AND squad_id IN ({','.join(map(str, squad_ids))})", (self.player_id,))
            await db.commit()

@save_to_command_log
@dataclass
class ApproveTransferCommand(Command[None]):
    invite_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT player_id, roster_id, roster_leave_id, is_accepted, is_bagger_clause FROM team_transfers WHERE id = ?", (self.invite_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem("Invite not found", status=404)
                player_id, roster_id, roster_leave_id, is_accepted, is_bagger_clause = row
            if not is_accepted:
                raise Problem("Invite has not been accepted by the player yet", status=400)
            if roster_leave_id:
                # check this before we move the player to the new team
                async with db.execute("SELECT id FROM team_members WHERE player_id = ? AND roster_id = ? AND leave_date IS ?", (player_id, roster_leave_id, None)) as cursor:
                    row = await cursor.fetchone()
                    if row is None:
                        raise Problem("Player is not currently on this roster", status=400)
                    team_member_id = row[0]
            else:
                team_member_id = None
            curr_time = int(datetime.now(timezone.utc).timestamp())
            # we use team_transfers table for transfers page, so don't delete the invite just set it to approved
            await db.execute("UPDATE team_transfers SET approval_status = ? WHERE id = ?", ("approved", self.invite_id,))
            await db.execute("INSERT INTO team_members(roster_id, player_id, join_date, is_bagger_clause) VALUES (?, ?, ?, ?)", (roster_id, player_id, curr_time, is_bagger_clause))
            if team_member_id:
                await db.execute("UPDATE team_members SET leave_date = ? WHERE id = ?", (curr_time, team_member_id))
                # get all team tournament rosters the player is in where the tournament hasn't ended yet
                async with db.execute("""SELECT p.squad_id FROM tournament_players p
                                    JOIN team_squad_registrations s ON p.squad_id = s.squad_id
                                    JOIN tournaments t ON p.tournament_id = t.id
                                    WHERE p.player_id = ? AND s.roster_id = ?
                                    AND (t.date_end > ? OR t.registrations_open = ?) AND t.team_members_only = ?
                                    AND p.is_bagger_clause = ?""",
                                    (player_id, roster_leave_id, curr_time, True, True, is_bagger_clause)) as cursor:
                    rows = await cursor.fetchall()
                    squad_ids: list[int] = [row[0] for row in rows]
                # if any of these squads the player was in previously are also linked to the new roster,
                # (such as when transferring between two rosters of same team), we don't want to remove them
                async with db.execute("""SELECT p.squad_id FROM tournament_players p
                                    JOIN team_squad_registrations s ON p.squad_id = s.squad_id
                                    JOIN tournaments t ON p.tournament_id = t.id
                                    WHERE p.player_id = ? AND s.roster_id = ?
                                    AND (t.date_end > ? OR t.registrations_open = ?) AND t.team_members_only = ?
                                    AND p.is_bagger_clause = ?""",
                                    (player_id, roster_id, curr_time, True, True, is_bagger_clause)) as cursor:
                    rows = await cursor.fetchall()
                    for row in rows:
                        if row[0] in squad_ids:
                            squad_ids.remove(row[0])
                # finally remove the player from all the tournaments they shouldn't be in
                await db.execute(f"DELETE FROM tournament_players WHERE player_id = ? AND squad_id IN ({','.join(map(str, squad_ids))})", (player_id,))

            # next we want to automatically add the transferred player to any team tournaments where that team is registered
            # and registrations are open
            async with db.execute("""SELECT s.squad_id, t.id FROM team_squad_registrations s
                                    JOIN tournaments t ON s.tournament_id = t.id
                                    WHERE t.teams_allowed = ? AND t.registrations_open = ?
                                    AND s.roster_id = ? AND NOT EXISTS (
                                        SELECT p.id FROM tournament_players p WHERE p.player_id = ? AND p.squad_id = s.squad_id
                                  )""", (True, True, roster_id, player_id)) as cursor:
                rows = await cursor.fetchall()
                squads: dict[int, int] = {}
                for row in rows:
                    squad, tournament = row
                    squads[tournament] = squad
            # if the player is already in some of these tournaments we don't want to add them again
            tournament_query = ','.join(map(str, squads.keys()))
            async with db.execute(f"SELECT squad_id, tournament_id FROM tournament_players WHERE player_id = ? AND is_bagger_clause = ? AND tournament_id IN ({tournament_query})",
                                  (player_id, is_bagger_clause)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    squad, tournament = row
                    if tournament in squads.keys():
                        del squads[tournament]
            insert_rows = [(player_id, tournament_id, squad_id, False, curr_time, False, None, False, False, None, False, is_bagger_clause,
                            False) for tournament_id, squad_id in squads.items()]
            await db.executemany("""INSERT INTO tournament_players(player_id, tournament_id, squad_id, is_squad_captain, timestamp, is_checked_in, mii_name, can_host, is_invite, selected_fc_id, 
                                 is_representative, is_bagger_clause, is_approved)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", insert_rows)
            await db.commit()

@save_to_command_log
@dataclass
class DenyTransferCommand(Command[None]):
    invite_id: int
    send_back: bool

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT player_id, roster_id, roster_leave_id, is_accepted FROM team_transfers WHERE id = ?", (self.invite_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem("Invite not found", status=404)
            # we would want to send the invite back to the player if for example they didn't specify a team they're leaving, otherwise just set it to denied
            if self.send_back:
                await db.execute("UPDATE team_transfers SET is_accepted = ? WHERE id = ?", (False, self.invite_id))
            else:
                await db.execute("UPDATE team_transfers SET approval_status = 'denied' WHERE id = ?", (self.invite_id,))
            await db.commit()

@dataclass
class ViewTransfersCommand(Command[TransferList]):
    filter: TransferFilter
    approval_status: Approval = "pending"
    
    async def handle(self, db_wrapper, s3_wrapper):
        transfers: list[TeamTransfer] = []

        filter = self.filter

        limit:int = 50
        offset:int = 0

        if filter.page is not None:
            offset = (filter.page - 1) * limit

        where_clauses: list[str] = []
        variable_parameters: list[Any] = []
        if filter.game is not None:
            where_clauses.append("(r1.game = ? OR r2.game = ?)")
            variable_parameters.extend([filter.game, filter.game])
        if filter.mode is not None:
            where_clauses.append("(r1.mode = ? OR r2.mode = ?)")
            variable_parameters.extend([filter.mode, filter.mode])
        if filter.team_id is not None:
            where_clauses.append("(t1.id = ? OR t2.id = ?)")
            variable_parameters.extend([filter.team_id, filter.team_id])
        if filter.roster_id is not None:
            where_clauses.append("(r1.id = ? OR r2.id = ?)")
            variable_parameters.extend([filter.roster_id, filter.roster_id])
        if filter.from_date is not None:
            where_clauses.append("i.date >= ?")
            variable_parameters.append(filter.from_date)
        if filter.to_date is not None:
            where_clauses.append("i.date < ?")
            variable_parameters.append(filter.to_date)
        
        where_clause_str = ""
        if len(where_clauses) > 0:
            where_clause_str = f"AND {' AND '.join(where_clauses)}"

        async with db_wrapper.connect() as db:
            # we need to do left outer joins with both the leave roster and the join roster,
            # since it's possible one of them doesn't exist.
            async with db.execute(f"""SELECT i.id, i.date, i.approval_status, i.is_bagger_clause,
                                    t1.id, t1.name, t1.tag, t1.color,
                                    i.roster_id, r1.name, r1.tag, r1.game, r1.mode, 
                                    t2.id, t2.name, t2.tag, t2.color,
                                    i.roster_leave_id, r2.name, r2.tag, r2.game, r2.mode, 
                                    p.id, p.name, p.country_code
                                    FROM team_transfers i
                                    LEFT OUTER JOIN team_rosters r1 ON i.roster_id = r1.id
                                    LEFT OUTER JOIN teams t1 ON r1.team_id = t1.id
                                    LEFT OUTER JOIN team_rosters r2 ON i.roster_leave_id = r2.id
                                    LEFT OUTER JOIN teams t2 ON r2.team_id = t2.id
                                    JOIN players p ON i.player_id = p.id
                                    WHERE i.is_accepted = 1 AND i.approval_status = ? {where_clause_str}
                                    ORDER BY i.id DESC LIMIT ? OFFSET ?""",
                                    (self.approval_status, *variable_parameters, limit, offset)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    (invite_id, date, approval_status, is_bagger_clause,
                     join_team_id, join_team_name, join_team_tag, join_team_color, 
                     join_roster_id, join_roster_name, join_roster_tag, join_roster_game, join_roster_mode,
                     leave_team_id, leave_team_name, leave_team_tag, leave_team_color, 
                     leave_roster_id, leave_roster_name, leave_roster_tag, leave_roster_game, leave_roster_mode,
                     player_id, player_name, player_country_code) = row
                    
                    if join_roster_id is not None:
                        if join_roster_name is None:
                            join_roster_name = join_team_name
                        if join_roster_tag is None:
                            join_roster_tag = join_team_tag

                    if leave_roster_id is not None:
                        if leave_roster_name is None:
                            leave_roster_name = leave_team_name
                        if leave_roster_tag is None:
                            leave_roster_tag = leave_team_tag

                    # in case the transfer is just a player leaving,
                    # need to get the game/mode from the roster that was left
                    game = join_roster_game
                    mode = join_roster_mode
                    if not game:
                        game = leave_roster_game
                    if not mode:
                        mode = leave_roster_mode

                    if leave_roster_id:
                        leave_roster = RosterBasic(leave_team_id, leave_team_name, leave_team_tag, leave_team_color, leave_roster_id,
                                                   leave_roster_name, leave_roster_tag)
                    else:
                        leave_roster = None

                    if join_roster_id:
                        join_roster = RosterBasic(join_team_id, join_team_name, join_team_tag, join_team_color, join_roster_id,
                                                     join_roster_name, join_roster_tag)
                    else:
                        join_roster = None

                    transfers.append(TeamTransfer(invite_id, date, is_bagger_clause, game, mode, player_id, player_name, player_country_code, approval_status, leave_roster, join_roster))

            async with db.execute(f"""SELECT COUNT(*)
                                    FROM team_transfers i
                                    LEFT OUTER JOIN team_rosters r1 ON i.roster_id = r1.id
                                    LEFT OUTER JOIN teams t1 ON r1.team_id = t1.id
                                    LEFT OUTER JOIN team_rosters r2 ON i.roster_leave_id = r2.id
                                    LEFT OUTER JOIN teams t2 ON r2.team_id = t2.id
                                    JOIN players p ON i.player_id = p.id
                                    WHERE i.is_accepted = 1 AND i.approval_status = ? {where_clause_str}""",
                                    (self.approval_status, *variable_parameters)) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                transfer_count = row[0]
                page_count = int(transfer_count / limit) + (1 if transfer_count % limit else 0)
        return TransferList(transfers, transfer_count, page_count)


@save_to_command_log
@dataclass
class ApproveTeamEditCommand(Command[None]):
    request_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT team_id, name, tag FROM team_edit_requests WHERE id = ?", (self.request_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem("Team edit request not found", status=404)
                team_id, name, tag = row
            await db.execute("UPDATE teams SET name = ?, tag = ? WHERE id = ?", (name, tag, team_id))
            await db.execute("UPDATE team_edit_requests SET approval_status = 'approved' WHERE id = ?", (self.request_id,))
            await db.commit()

@save_to_command_log
@dataclass
class DenyTeamEditCommand(Command[None]):
    request_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("UPDATE team_edit_requests SET approval_status = 'denied' WHERE id = ?", (self.request_id,)) as cursor:
                rowcount = cursor.rowcount
                if rowcount == 0:
                    raise Problem("Team edit request not found", status=404)
            await db.commit()

@dataclass
class ListTeamEditRequestsCommand(Command[list[TeamEditRequest]]):
    approval_status: Approval

    async def handle(self, db_wrapper, s3_wrapper):
        requests: list[TeamEditRequest] = []
        async with db_wrapper.connect() as db:
            async with db.execute("""SELECT r.id, r.team_id, t.name, t.tag, r.name, r.tag, t.color, r.date, r.approval_status FROM team_edit_requests r
                                  JOIN teams t ON r.team_id = t.id
                                  WHERE r.approval_status = ?""", (self.approval_status,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    requests.append(TeamEditRequest(*row))
        return requests

@save_to_command_log
@dataclass
class RequestEditRosterCommand(Command[None]):
    roster_id: int
    team_id: int
    name: str | None
    tag: str | None

    async def handle(self, db_wrapper, s3_wrapper):
        name = self.name
        tag = self.tag
        async with db_wrapper.connect() as db:
            # check if this roster has made a request in the last 90 days
            async with db.execute("SELECT date FROM roster_edit_requests WHERE roster_id = ? AND date > ? AND approval_status != 'denied' LIMIT 1",
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
                # sync name/tag with team if same as team
                if name == team_name:
                    name = None
                if tag == team_tag:
                    tag = None
                if name == roster_name and tag == roster_tag:
                    raise Problem("At least one of the roster name or tag must be different from their current values", status=400)
            if name:
                async with db.execute("SELECT id FROM team_rosters WHERE id != ? AND team_id = ? AND game = ? AND mode = ? AND name IS ?",
                                    (self.roster_id, self.team_id, game, mode, name)) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        raise Problem("Another roster for this game and mode has the same name as the specified name", status=400)
            creation_date = int(datetime.now(timezone.utc).timestamp())
            await db.execute("INSERT INTO roster_edit_requests(roster_id, name, tag, date, approval_status) VALUES (?, ?, ?, ?, ?)", 
                             (self.roster_id, name, tag, creation_date, "pending"))
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

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT roster_id, name, tag FROM roster_edit_requests WHERE id = ?", (self.request_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Roster edit request not found", status=404)
                roster_id, name, tag = row
            await db.execute("UPDATE team_rosters SET name = ?, tag = ? WHERE id = ?", (name, tag, roster_id))
            await db.execute("UPDATE roster_edit_requests SET approval_status = 'approved' WHERE id = ?", (self.request_id,))
            await db.commit()

@save_to_command_log
@dataclass
class DenyRosterEditCommand(Command[None]):
    request_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("UPDATE roster_edit_requests SET approval_status = 'denied' WHERE id = ?", (self.request_id,)) as cursor:
                rowcount = cursor.rowcount
                if rowcount == 0:
                    raise Problem("Roster edit request not found", status=404)
            await db.commit()

@dataclass
class ListRosterEditRequestsCommand(Command[list[RosterEditRequest]]):
    approval_status: Approval

    async def handle(self, db_wrapper, s3_wrapper):
        requests: list[RosterEditRequest] = []
        async with db_wrapper.connect() as db:
            async with db.execute("""SELECT r.id, r.roster_id, t.id, t.name, t.tag, tr.name, tr.tag, r.name, r.tag, t.color, r.date, r.approval_status FROM roster_edit_requests r
                                  JOIN team_rosters tr ON r.roster_id = tr.id
                                  JOIN teams t ON tr.team_id = t.id
                                  WHERE r.approval_status = ?""", (self.approval_status,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    request_id, roster_id, team_id, team_name, team_tag, roster_name, roster_tag, request_name, request_tag, team_color, date, approval_status = row
                    if roster_name is None:
                        roster_name = team_name
                    if roster_tag is None:
                        roster_tag = team_tag
                    if request_name is None:
                        request_name = team_name
                    if request_tag is None:
                        request_tag = team_tag
                    requests.append(RosterEditRequest(request_id, roster_id, team_id, team_name, team_tag, roster_name, roster_tag,
                                                      request_name, request_tag, team_color, date, approval_status))
        return requests

@save_to_command_log
@dataclass
class ForceTransferPlayerCommand(Command[None]):
    player_id: int
    roster_id: int
    team_id: int
    roster_leave_id: int | None
    is_bagger_clause: bool

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT id, game FROM team_rosters WHERE id = ? AND team_id = ?", (self.roster_id, self.team_id)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Roster not found", status=404)
                game = row[1]
                if self.is_bagger_clause and game != "mkw":
                    raise Problem("Cannot make players baggers for games other than MKW", status=400)
            async with db.execute("SELECT id FROM friend_codes WHERE game = ? AND player_id = ? AND is_active = ?", (game, self.player_id, True)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Player has no friend codes for this game", status=400)
            if self.roster_leave_id:
                # check this before we move the player to the new team
                async with db.execute("SELECT id FROM team_members WHERE player_id = ? AND roster_id = ? AND leave_date IS ?", (self.player_id, self.roster_leave_id, None)) as cursor:
                    row = await cursor.fetchone()
                    if row is None:
                        raise Problem("Player is not currently on this roster", status=400)
                    team_member_id = row[0]
            else:
                team_member_id = None
            async with db.execute("SELECT id FROM team_members WHERE player_id = ? AND roster_id = ? AND leave_date IS ?", (self.player_id, self.roster_id, None)) as cursor:
                row = await cursor.fetchone()
                if row:
                    raise Problem("Player is already on this roster", status=400)
            curr_time = int(datetime.now(timezone.utc).timestamp())
            await db.execute("INSERT INTO team_members(roster_id, player_id, join_date, is_bagger_clause) VALUES (?, ?, ?, ?)", 
                             (self.roster_id, self.player_id, curr_time, self.is_bagger_clause))
            await db.execute("""INSERT INTO team_transfers(player_id, roster_id, date, roster_leave_id, is_accepted, approval_status, is_bagger_clause)
                             VALUES(?, ?, ?, ?, ?, ?, ?)""", (self.player_id, self.roster_id, curr_time, self.roster_leave_id, True, "approved", self.is_bagger_clause))
            if team_member_id:
                await db.execute("UPDATE team_members SET leave_date = ? WHERE id = ?", (curr_time, team_member_id))
                # get all team tournament rosters the player is in where the tournament hasn't ended yet
                async with db.execute("""SELECT p.squad_id FROM tournament_players p
                                    JOIN team_squad_registrations s ON p.squad_id = s.squad_id
                                    JOIN tournaments t ON p.tournament_id = t.id
                                    WHERE p.player_id = ? AND s.roster_id = ?
                                    AND (t.date_end > ? OR t.registrations_open = ?) AND t.team_members_only = ?
                                    AND p.is_bagger_clause = ?""",
                                    (self.player_id, self.roster_leave_id, curr_time, True, True, self.is_bagger_clause)) as cursor:
                    rows = await cursor.fetchall()
                    squad_ids: list[int] = [row[0] for row in rows]
                # if any of these squads the player was in previously are also linked to the new roster,
                # (such as when transferring between two rosters of same team), we don't want to remove them
                async with db.execute("""SELECT p.squad_id FROM tournament_players p
                                    JOIN team_squad_registrations s ON p.squad_id = s.squad_id
                                    JOIN tournaments t ON p.tournament_id = t.id
                                    WHERE p.player_id = ? AND s.roster_id = ?
                                    AND (t.date_end > ? OR t.registrations_open = ?) AND t.team_members_only = ?
                                    AND p.is_bagger_clause = ?""",
                                    (self.player_id, self.roster_id, curr_time, True, True, self.is_bagger_clause)) as cursor:
                    rows = await cursor.fetchall()
                    for row in rows:
                        if row[0] in squad_ids:
                            squad_ids.remove(row[0])
                # finally remove the player from all the tournaments they shouldn't be in
                await db.execute(f"DELETE FROM tournament_players WHERE player_id = ? AND squad_id IN ({','.join(map(str, squad_ids))})", (self.player_id,))

            # next we want to automatically add the transferred player to any team tournaments where that team is registered
            # and registrations are open
            async with db.execute("""SELECT s.squad_id, t.id FROM team_squad_registrations s
                                    JOIN tournaments t ON s.tournament_id = t.id
                                    WHERE t.teams_allowed = ? AND t.registrations_open = ?
                                    AND s.roster_id = ? AND NOT EXISTS (
                                        SELECT p.id FROM tournament_players p 
                                        WHERE p.player_id = ? AND p.squad_id = s.squad_id
                                    )""", (True, True, self.roster_id, self.player_id)) as cursor:
                rows = await cursor.fetchall()
                squads: dict[int, int] = {}
                for row in rows:
                    squad, tournament = row
                    squads[tournament] = squad
            # if the player is already in some of these tournaments we don't want to add them again
            tournament_query = ','.join(map(str, squads.keys()))
            async with db.execute(f"SELECT squad_id, tournament_id FROM tournament_players WHERE player_id = ? AND tournament_id IN ({tournament_query})",
                                  (self.player_id,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    squad, tournament = row
                    if tournament in squads.keys():
                        del squads[tournament]
            insert_rows = [(self.player_id, tournament_id, squad_id, False, curr_time, False, None, False, False, None, False, self.is_bagger_clause,
                            False) for tournament_id, squad_id in squads.items()]
            await db.executemany("""INSERT INTO tournament_players(player_id, tournament_id, squad_id, is_squad_captain, timestamp, is_checked_in, mii_name, can_host, is_invite, selected_fc_id, 
                                 is_representative, is_bagger_clause, is_approved)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", insert_rows)
            await db.commit()

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

@dataclass
class ListTeamsCommand(Command[List[Team]]):
    filter: TeamFilter
    approved: bool = True

    async def handle(self, db_wrapper, s3_wrapper):
        filter = self.filter
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

            # check both the team and team_roster fields with the same name for a match
            def append_team_roster_like_filter(filter_value: Any, column_name: str):
                if filter_value is not None:
                    where_clauses.append(f"(t.{column_name} LIKE ? OR r.{column_name} LIKE ?)")
                    variable_parameters.extend([f"%{filter_value}%", f"%{filter_value}%"])

            append_team_roster_like_filter(filter.name, "name")
            append_team_roster_like_filter(filter.tag, "tag")
            append_equal_filter(filter.game, "r.game")
            append_equal_filter(filter.mode, "r.mode")
            append_equal_filter(filter.language, "t.language")
            append_equal_filter(filter.is_recruiting, "r.is_recruiting")
            append_equal_filter(filter.is_historical, "t.is_historical")
            append_equal_filter(filter.is_active, "r.is_active")

            if self.approved:
                append_equal_filter("approved", "t.approval_status")
                append_equal_filter("approved", "r.approval_status")
            else:
                append_not_equal_filter("approved", "t.approval_status")
                append_not_equal_filter("approved", "r.approval_status")

            where_clause = "" if not where_clauses else f" WHERE {' AND '.join(where_clauses)}"
            order_by = 't.creation_date' if filter.sort_by_newest else 't.name'
            desc = 'DESC' if filter.sort_by_newest else ''
            teams_query = f"""  SELECT t.id, t.name, t.tag, t.description, t.creation_date, t.language, t.color, t.logo,
                                t.approval_status, t.is_historical, r.id, r.game, r.mode, r.name, r.tag, r.creation_date,
                                r.is_recruiting, r.is_active, r.approval_status
                                FROM teams t JOIN team_rosters r ON t.id = r.team_id
                                {where_clause}
                                ORDER BY {order_by} COLLATE NOCASE {desc}
                                """
            teams: dict[int, Team] = {}
            async with db.execute(teams_query, variable_parameters) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    (tid, tname, ttag, description, tdate, lang, color, logo, tapprove, is_historical, rid,
                      game, mode, rname, rtag, rdate, is_recruiting, is_active, rapprove) = row
                    roster = TeamRoster(rid, tid, game, mode, rname if rname else tname, rtag if rtag else ttag, rdate, is_recruiting, is_active, rapprove, color, [], [])
                    if tid in teams:
                        team: Team = teams[tid]
                        team.rosters.append(roster)
                        continue
                    team = Team(tid, tname, ttag, description, tdate, lang, color, logo, tapprove, is_historical, [roster], [])
                    teams[tid] = team
            team_list = list(teams.values())
            return team_list
        
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
            rosters_query = f"""
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
                            JOIN tournament_squads s ON tsr.squad_id = s.id
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
                                )""", variable_parameters) as cursor:
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
            
            async with db.execute(f"""SELECT DISTINCT f.id, f.player_id, f.game, f.fc, f.is_verified, f.is_primary, f.is_active
                                  FROM friend_codes f
                                  JOIN players p ON f.player_id = p.id
                                  JOIN team_members m ON p.id = m.player_id
                                  WHERE f.game = ? AND m.roster_id IN (
                                    SELECT tr.id
                                    {rosters_query}
                                  )""", (self.game, *variable_parameters)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    fc_id, player_id, game, fc, is_verified, is_primary, is_active = row
                    player_fcs = fc_dict.get(player_id, None)
                    if player_fcs:
                        player_fcs.append(FriendCode(fc_id, fc, game, player_id, bool(is_verified), bool(is_primary), is_active=bool(is_active)))
            return rosters

@save_to_command_log
@dataclass
class MergeTeamsCommand(Command[None]):
    from_team_id: int
    to_team_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        if self.from_team_id == self.to_team_id:
            raise Problem("Team IDs are equal", status=400)
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT name, tag FROM teams WHERE id = ?", (self.from_team_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem(f"Team ID {self.from_team_id} not found", status=404)
                old_name, old_tag = row
            async with db.execute("SELECT id FROM teams WHERE id = ?", (self.to_team_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem(f"Team ID {self.to_team_id} not found", status=404)
            # don't want to change the name/tag of a roster to the new team's name if it's the default value
            await db.execute("UPDATE team_rosters SET name = ? WHERE team_id = ? AND name IS NULL", (old_name, self.from_team_id))
            await db.execute("UPDATE team_rosters SET tag = ? WHERE team_id = ? AND tag IS NULL", (old_tag, self.from_team_id))

            await db.execute("UPDATE team_rosters SET team_id = ? WHERE team_id = ?", (self.to_team_id, self.from_team_id))
            await db.execute("DELETE FROM user_team_roles WHERE team_id = ?", (self.from_team_id,))
            await db.execute("DELETE FROM team_edit_requests WHERE team_id = ?", (self.from_team_id,))
            await db.execute("DELETE FROM teams WHERE id = ?", (self.from_team_id,))
            await db.commit()