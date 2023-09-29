from dataclasses import dataclass
from datetime import datetime

from common.data.commands import Command, save_to_command_log
from common.data.models import *


@save_to_command_log
@dataclass
class CreateTeamCommand(Command[None]):
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
                async with db.execute("SELECT COUNT(id) FROM team_rosters WHERE name = ? OR tag = ?", (self.name, self.tag)) as cursor:
                    row = await cursor.fetchone()
                    assert row is not None
                    if row[0] > 0:
                        raise Problem('An existing team already has this name or tag', status=400)
            creation_date = int(datetime.utcnow().timestamp())
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
            
            # get all rosters for our team
            rosters: list[TeamRoster] = []
            roster_dict: dict[int, TeamRoster] = {}
            async with db.execute("SELECT id, game, mode, name, tag, creation_date, is_recruiting, approval_status FROM team_rosters WHERE team_id = ?",
                (self.team_id,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    roster_id, game, mode, roster_name, roster_tag, roster_date, is_recruiting, roster_approval_status = row
                    if roster_name is None:
                        roster_name = team_name
                    if roster_tag is None:
                        roster_tag = team_tag
                    curr_roster = TeamRoster(roster_id, self.team_id, game, mode, roster_name, roster_tag, roster_date, is_recruiting, roster_approval_status, [], [])
                    rosters.append(curr_roster)
                    roster_dict[curr_roster.id] = curr_roster
            
            team_members: list[PartialTeamMember] = []
            # get all current team members who are in a roster that belongs to our team
            roster_id_query = ','.join(map(str, roster_dict.keys()))
            async with db.execute(f"""SELECT player_id, roster_id, join_date
                                    FROM team_members
                                    WHERE roster_id IN ({roster_id_query}) AND leave_date IS ?
                                    """, (None,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    player_id, roster_id, join_date = row
                    curr_team_member = PartialTeamMember(player_id, roster_id, join_date)
                    team_members.append(curr_team_member)

            team_invites: list[PartialTeamMember] = []
            # get all invited players to a roster on our team
            async with db.execute(f"""SELECT player_id, roster_id, date
                                  FROM roster_invites
                                  WHERE roster_id IN ({roster_id_query})""") as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    curr_invited_player = PartialTeamMember(*row)
                    team_invites.append(curr_invited_player)

            player_dict: dict[int, PartialPlayer] = {}

            if len(team_members) > 0 or len(team_invites) > 0:
                # get info about all players who are in/invited to at least 1 roster on our team
                member_id_query = ','.join(set([str(m.player_id) for m in team_members] + [str(m.player_id) for m in team_invites]))
                async with db.execute(f"SELECT id, name, country_code, is_banned, discord_id FROM players WHERE id IN ({member_id_query})") as cursor:
                    rows = await cursor.fetchall()
                    for row in rows:
                        player_id, player_name, country, is_banned, discord_id = row
                        player_dict[player_id] = PartialPlayer(player_id, player_name, country, bool(is_banned), discord_id, [])

                # get all friend codes for members of our team that are from a game that our team has a roster for
                game_query = ','.join(set([f"'{r.game}'" for r in rosters]))
                async with db.execute(f"SELECT player_id, game, fc, is_verified, is_primary FROM friend_codes WHERE player_id IN ({member_id_query}) AND game IN ({game_query})") as cursor:
                    rows = await cursor.fetchall()
                    for row in rows:
                        player_id, game, fc, is_verified, is_primary = row
                        curr_fc = FriendCode(fc, game, player_id, bool(is_verified), bool(is_primary))
                        player_dict[player_id].friend_codes.append(curr_fc)

            for member in team_members:
                curr_roster = roster_dict[member.roster_id]
                p = player_dict[member.player_id]
                curr_player = RosterPlayerInfo(p.player_id, p.name, p.country_code, p.is_banned, p.discord_id, member.join_date,
                    [fc for fc in p.friend_codes if fc.game == curr_roster.game]) # only add FCs that are for the same game as current roster
                curr_roster.players.append(curr_player)

            for invite in team_invites:
                curr_roster = roster_dict[invite.roster_id]
                p = player_dict[invite.player_id]
                curr_player = RosterInvitedPlayer(p.player_id, p.name, p.country_code, p.is_banned, p.discord_id, invite.join_date,
                    [fc for fc in p.friend_codes if fc.game == curr_roster.game]) # only add FCs that are for the same game as current roster
                curr_roster.invites.append(curr_player) 

            async with db.execute("""SELECT p.id, p.name, p.country_code, p.is_hidden, p.is_shadow, p.is_banned, p.discord_id FROM players p
                JOIN users u ON u.player_id = p.id
                JOIN user_team_roles ur ON ur.user_id = u.id
                WHERE ur.team_id = ? AND ur.role_id = 0""", (self.team_id,)) as cursor:
                rows = await cursor.fetchall()
                team.managers = [Player(*row) for row in rows]
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
            creation_date = int(datetime.utcnow().timestamp())
            await db.execute("INSERT INTO team_edit_requests(team_id, name, tag, date, approval_status) VALUES(?, ?, ?, ?, ?)",
                            (self.team_id, self.name, self.tag, creation_date, "pending"))
            await db.commit()

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
            async with db.execute("SELECT name, tag FROM teams WHERE id = ?", (self.team_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem('No team found', status=404)
                team_name, team_tag = row
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
            creation_date = int(datetime.utcnow().timestamp())
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
            async with db.execute("SELECT name, tag FROM teams WHERE id = ?", (self.team_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem('No team found', status=404)
                team_name, team_tag = row
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
                async with db.execute("SELECT name FROM team_rosters WHERE team_id = ? AND game = ? AND mode = ? AND name IS ? AND roster_id != ?", (self.team_id, game, mode, self.name, self.roster_id)) as cursor:
                    row = await cursor.fetchone()
                    if row is not None:
                        raise Problem('Only one roster per game/mode may use the same name', status=400)
            await db.execute("UPDATE team_rosters SET team_id = ?, name = ?, tag = ?, is_recruiting = ?, is_active = ?, approval_status = ?",
                             (self.team_id, self.name, self.tag, self.is_recruiting, self.is_active, self.approval_status))
            await db.commit()

@save_to_command_log
@dataclass
class InvitePlayerCommand(Command[None]):
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
            async with db.execute("SELECT id FROM players WHERE id = ?", (self.player_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Player not found", status=404)
            async with db.execute("SELECT id FROM team_members WHERE roster_id = ? AND leave_date IS ?", (self.roster_id, None)) as cursor:
                row = await cursor.fetchone()
                if row:
                    raise Problem("Player is already on this roster", status=400)
            async with db.execute("SELECT COUNT(id) FROM roster_invites WHERE player_id = ? AND roster_id = ?", (self.player_id, self.roster_id)) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                num_invites = row[0]
                if num_invites > 0:
                    raise Problem("Player has already been invited", status=400)
            creation_date = int(datetime.utcnow().timestamp())
            await db.execute("INSERT INTO roster_invites(player_id, roster_id, date, is_accepted) VALUES (?, ?, ?, ?)", (self.player_id, self.roster_id, creation_date, False))
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
            async with db.execute("DELETE FROM roster_invites WHERE player_id = ? AND roster_id = ?", (self.player_id, self.roster_id)) as cursor:
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
            async with db.execute("SELECT r.game, i.player_id FROM roster_invites i JOIN team_rosters r ON i.roster_id = r.id WHERE i.id = ?", (self.invite_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem("No invite found", status=404)
                game, invite_player_id = row
                if self.player_id != invite_player_id:
                    raise Problem("Cannot accept invite for another player", status=400)
            # make sure that we are actually in the roster we're leaving
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
            await db.execute("UPDATE roster_invites SET roster_leave_id = ?, is_accepted = ? WHERE id = ?", (self.roster_leave_id, True, self.invite_id))
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
            async with db.execute("SELECT player_id FROM roster_invites WHERE id = ?", (self.invite_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem("No invite found", status=404)
                invite_player_id = row[0]
                if self.player_id != invite_player_id and not self.is_privileged:
                    raise Problem("Cannot decline invite for another player", status=400)
            await db.execute("DELETE FROM roster_invites WHERE id = ?", (self.invite_id,))
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
            leave_date = int(datetime.utcnow().timestamp())
            await db.execute("UPDATE team_members SET leave_date = ? WHERE id = ?", (leave_date, team_member_id))

@save_to_command_log
@dataclass
class ApproveTransferCommand(Command[None]):
    invite_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT player_id, roster_id, roster_leave_id, is_accepted FROM roster_invites WHERE id = ?", (self.invite_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem("Invite not found", status=404)
                player_id, roster_id, roster_leave_id, is_accepted = row
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
            curr_time = int(datetime.utcnow().timestamp())
            await db.execute("DELETE FROM roster_invites WHERE id = ?", (self.invite_id,))
            await db.execute("INSERT INTO team_members(roster_id, player_id, join_date) VALUES (?, ?, ?)", (roster_id, player_id, curr_time))
            if team_member_id:
                await db.execute("UPDATE team_members SET leave_date = ? WHERE id = ?", (curr_time, team_member_id))
                # get all team tournament rosters the player is in where the tournament hasn't ended yet
                async with db.execute("""SELECT p.squad_id FROM tournament_players p
                                    JOIN team_squad_registrations s ON p.squad_id = s.squad_id
                                    JOIN tournaments t ON p.tournament_id = t.id
                                    WHERE p.player_id = ? AND s.roster_id = ?
                                    AND (t.date_end > ? OR t.registrations_open = ?) AND t.team_members_only = ?""",
                                    (player_id, roster_leave_id, curr_time, True, True)) as cursor:
                    rows = await cursor.fetchall()
                    squad_ids: list[int] = [row[0] for row in rows]
                # if any of these squads the player was in previously are also linked to the new roster,
                # (such as when transferring between two rosters of same team), we don't want to remove them
                async with db.execute("""SELECT p.squad_id FROM tournament_players p
                                    JOIN team_squad_registrations s ON p.squad_id = s.squad_id
                                    JOIN tournaments t ON p.tournament_id = t.id
                                    WHERE p.player_id = ? AND s.roster_id = ?
                                    AND (t.date_end > ? OR t.registrations_open = ?) AND t.team_members_only = ?""",
                                    (player_id, roster_id, curr_time, True, True)) as cursor:
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
                                    AND s.roster_id = ?""", (True, True, roster_id)) as cursor:
                rows = await cursor.fetchall()
                #squads = [(row[0], row[1]) for row in rows]
                squads: dict[int, int] = {}
                for row in rows:
                    squad, tournament = row
                    squads[tournament] = squad
            # if the player is already in some of these tournaments we don't want to add them again
            tournament_query = ','.join(map(str, squads.keys()))
            async with db.execute(f"SELECT squad_id, tournament_id FROM tournament_players WHERE player_id = ? AND tournament_id IN ({tournament_query})",
                                  (player_id,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    squad, tournament = row
                    if tournament in squads.keys():
                        del squads[tournament]
            insert_rows = [(player_id, tournament_id, squad_id, False, curr_time, False, None, False, False, None, False) for tournament_id, squad_id in squads.items()]
            await db.executemany("""INSERT INTO tournament_players(player_id, tournament_id, squad_id, is_squad_captain, timestamp, is_checked_in, mii_name, can_host, is_invite, selected_fc_id, is_representative)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", insert_rows)
            await db.commit()

@save_to_command_log
@dataclass
class DenyTransferCommand(Command[None]):
    invite_id: int
    send_back: bool

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT player_id, roster_id, roster_leave_id, is_accepted FROM roster_invites WHERE id = ?", (self.invite_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem("Invite not found", status=404)
            # we would want to send the invite back to the player if for example they didn't specify a team they're leaving, otherwise can just delete it
            if self.send_back:
                await db.execute("UPDATE roster_invites SET is_accepted = ? WHERE id = ?", (False, self.invite_id))
            else:
                await db.execute("DELETE FROM roster_invites WHERE id = ?", (self.invite_id,))
            await db.commit()

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
        requests = []
        async with db_wrapper.connect() as db:
            async with db.execute("""SELECT r.id, r.team_id, t.name, t.tag, r.name, r.tag, r.date, r.approval_status FROM team_edit_requests r
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
            async with db.execute("SELECT t.name, t.tag, r.game, r.mode FROM team_rosters r JOIN teams t ON r.team_id = t.id WHERE r.id = ? AND r.team_id = ?", (self.roster_id, self.team_id)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Roster not found", status=404)
                team_name, team_tag, game, mode = row
                # sync name/tag with team if same as team
                if name == team_name:
                    name = None
                if tag == team_tag:
                    tag = None
            if name:
                async with db.execute("SELECT id FROM team_rosters WHERE id != ? AND team_id = ? AND game = ? AND mode = ? AND name IS ?",
                                    (self.roster_id, self.team_id, game, mode, name)) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        raise Problem("Another roster for this game and mode has the same name as the specified name", status=400)
            creation_date = int(datetime.utcnow().timestamp())
            await db.execute("INSERT INTO roster_edit_requests(roster_id, name, tag, date, approval_status) VALUES (?, ?, ?, ?, ?)", 
                             (self.roster_id, name, tag, creation_date, "pending"))
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
        requests = []
        async with db_wrapper.connect() as db:
            async with db.execute("""SELECT r.id, r.roster_id, t.id, t.name, t.tag, tr.name, tr.tag, r.name, r.tag, r.date, r.approval_status FROM roster_edit_requests r
                                  JOIN team_rosters tr ON r.roster_id = tr.id
                                  JOIN teams t ON tr.team_id = t.id
                                  WHERE r.approval_status = ?""", (self.approval_status,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    requests.append(RosterEditRequest(*row))
        return requests

@save_to_command_log
@dataclass
class ForceTransferPlayerCommand(Command[None]):
    player_id: int
    roster_id: int
    team_id: int
    roster_leave_id: int | None

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT id FROM team_rosters WHERE id = ? AND team_id = ?", (self.roster_id, self.team_id)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Roster not found", status=404)
            if self.roster_leave_id:
                # check this before we move the player to the new team
                async with db.execute("SELECT id FROM team_members WHERE player_id = ? AND roster_id = ? AND leave_date IS ?", (self.player_id, self.roster_leave_id, None)) as cursor:
                    row = await cursor.fetchone()
                    if row is None:
                        raise Problem("Player is not currently on this roster", status=400)
                    team_member_id = row[0]
            else:
                team_member_id = None
            curr_time = int(datetime.utcnow().timestamp())
            await db.execute("INSERT INTO team_members(roster_id, player_id, join_date) VALUES (?, ?, ?)", (self.roster_id, self.player_id, curr_time))
            if team_member_id:
                await db.execute("UPDATE team_members SET leave_date = ? WHERE id = ?", (curr_time, team_member_id))
                # get all team tournament rosters the player is in where the tournament hasn't ended yet
                async with db.execute("""SELECT p.squad_id FROM tournament_players p
                                    JOIN team_squad_registrations s ON p.squad_id = s.squad_id
                                    JOIN tournaments t ON p.tournament_id = t.id
                                    WHERE p.player_id = ? AND s.roster_id = ?
                                    AND (t.date_end > ? OR t.registrations_open = ?) AND t.team_members_only = ?""",
                                    (self.player_id, self.roster_leave_id, curr_time, True, True)) as cursor:
                    rows = await cursor.fetchall()
                    squad_ids: list[int] = [row[0] for row in rows]
                # if any of these squads the player was in previously are also linked to the new roster,
                # (such as when transferring between two rosters of same team), we don't want to remove them
                async with db.execute("""SELECT p.squad_id FROM tournament_players p
                                    JOIN team_squad_registrations s ON p.squad_id = s.squad_id
                                    JOIN tournaments t ON p.tournament_id = t.id
                                    WHERE p.player_id = ? AND s.roster_id = ?
                                    AND (t.date_end > ? OR t.registrations_open = ?) AND t.team_members_only = ?""",
                                    (self.player_id, self.roster_id, curr_time, True, True)) as cursor:
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
                                    AND s.roster_id = ?""", (True, True, self.roster_id)) as cursor:
                rows = await cursor.fetchall()
                #squads = [(row[0], row[1]) for row in rows]
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
            insert_rows = [(self.player_id, tournament_id, squad_id, False, curr_time, False, None, False, False, None, False) for tournament_id, squad_id in squads.items()]
            await db.executemany("""INSERT INTO tournament_players(player_id, tournament_id, squad_id, is_squad_captain, timestamp, is_checked_in, mii_name, can_host, is_invite, selected_fc_id, is_representative)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", insert_rows)
            await db.commit()

@save_to_command_log
@dataclass
class EditTeamMemberCommand(Command[None]):
    id: int
    roster_id: int
    team_id: int
    join_date: int | None
    leave_date: int | None

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("""SELECT join_date FROM team_members m
                                    JOIN team_rosters r ON m.roster_id = r.id
                                    JOIN teams t ON r.team_id = t.id
                                    WHERE m.id = ? AND m.roster_id = ? AND t.team_id = ?
                                    """, (self.id, self.roster_id, self.team_id)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Team member not found", status=404)
                member_join_date = row[0]
                if not self.join_date:
                    self.join_date = member_join_date
            await db.execute("UPDATE team_members SET join_date = ?, leave_date = ? WHERE id = ?", (self.join_date, self.leave_date, self.id))
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
                    variable_parameters.extend([filter_value, filter_value])

            append_team_roster_like_filter(filter.name, "name")
            append_team_roster_like_filter(filter.tag, "tag")
            append_equal_filter(filter.game, "r.game")
            append_equal_filter(filter.mode, "r.mode")
            append_equal_filter(filter.language, "t.language")
            append_equal_filter(filter.is_historical, "t.is_historical")
            append_equal_filter(filter.is_recruiting, "r.is_recruiting")
            if self.approved:
                append_equal_filter("approved", "t.approval_status")
                append_equal_filter("approved", "r.approval_status")
            else:
                append_not_equal_filter("approved", "t.approval_status")
                append_not_equal_filter("approved", "r.approval_status")
            append_equal_filter(True, "r.is_active")

            where_clause = "" if not where_clauses else f" WHERE {' AND '.join(where_clauses)}"
            teams_query = f"""  SELECT t.id, t.name, t.tag, t.description, t.creation_date, t.language, t.color, t.logo,
                                t.approval_status, t.is_historical, r.id, r.game, r.mode, r.name, r.tag, r.creation_date,
                                r.is_recruiting, r.approval_status
                                FROM teams t JOIN team_rosters r ON t.id = r.team_id
                                {where_clause}
                                """
            teams: dict[int, Team] = {}
            async with db.execute(teams_query, variable_parameters) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    tid, tname, ttag, description, tdate, lang, color, logo, tapprove, is_historical, rid, game, mode, rname, rtag, rdate, is_recruiting, rapprove = row
                    roster = TeamRoster(rid, tid, game, mode, rname if rname else tname, rtag if rtag else ttag, rdate, is_recruiting, rapprove, [], [])
                    if tid in teams:
                        team: Team = teams[tid]
                        team.rosters.append(roster)
                        continue
                    team = Team(tid, tname, ttag, description, tdate, lang, color, logo, tapprove, is_historical, [roster], [])
                    teams[tid] = team
            team_list = list(teams.values())
            return team_list