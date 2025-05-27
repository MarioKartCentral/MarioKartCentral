from dataclasses import dataclass
from datetime import timezone
from common.data.commands import Command, save_to_command_log
from common.data.models import *

@save_to_command_log
@dataclass
class ApproveTransferCommand(Command[None]):
    invite_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT player_id, roster_id, roster_leave_id, is_accepted, is_bagger_clause, approval_status FROM team_transfers WHERE id = ?", (self.invite_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem("Invite not found", status=404)
                player_id, roster_id, roster_leave_id, is_accepted, is_bagger_clause, approval_status = row
            if not is_accepted:
                raise Problem("Invite has not been accepted by the player yet", status=400)
            if roster_leave_id:
                # check this before we move the player to the new team
                async with db.execute("SELECT id FROM team_members WHERE player_id = ? AND roster_id = ? AND leave_date IS ? AND is_bagger_clause = ?",
                                      (player_id, roster_leave_id, None, is_bagger_clause)) as cursor:
                    row = await cursor.fetchone()
                    if row is None:
                        raise Problem("Player is not currently on the roster they are leaving", status=400)
                    team_member_id = row[0]
            else:
                team_member_id = None
            if approval_status == "approved":
                raise Problem("Transfer is already approved", status=400)
            curr_time = int(datetime.now(timezone.utc).timestamp())
            # we use team_transfers table for transfers page, so don't delete the invite just set it to approved
            await db.execute("UPDATE team_transfers SET approval_status = ? WHERE id = ?", ("approved", self.invite_id,))
            await db.execute("INSERT INTO team_members(roster_id, player_id, join_date, is_bagger_clause) VALUES (?, ?, ?, ?)", (roster_id, player_id, curr_time, is_bagger_clause))
            # remove player from the same roster as the opposite bagger type, if exists
            async with db.execute("UPDATE team_members SET leave_date = ? WHERE player_id = ? AND roster_id = ? AND leave_date IS ? AND is_bagger_clause = ?", 
                             (curr_time, player_id, roster_id, None, not is_bagger_clause)) as cursor:
                rowcount = cursor.rowcount
                if rowcount == 1:
                    await db.execute("""INSERT INTO team_transfers(player_id, roster_id, date, roster_leave_id, is_accepted, approval_status, is_bagger_clause)
                                     VALUES(?, ?, ?, ?, ?, ?, ?)""", (player_id, None, curr_time, roster_id, True, "approved", not is_bagger_clause))
            if team_member_id:
                await db.execute("UPDATE team_members SET leave_date = ? WHERE id = ?", (curr_time, team_member_id))
                # get all team tournament rosters the player is in where the tournament hasn't ended yet
                async with db.execute("""SELECT p.registration_id FROM tournament_players p
                                    JOIN team_squad_registrations s ON p.registration_id = s.registration_id
                                    JOIN tournaments t ON p.tournament_id = t.id
                                    WHERE p.player_id = ? AND s.roster_id = ?
                                    AND (t.date_end > ? OR t.registrations_open = ?) AND t.team_members_only = ?
                                    AND p.is_bagger_clause = ?""",
                                    (player_id, roster_leave_id, curr_time, True, True, is_bagger_clause)) as cursor:
                    rows = await cursor.fetchall()
                    registration_ids: list[int] = [row[0] for row in rows]
                # if any of these squads the player was in previously are also linked to the new roster,
                # (such as when transferring between two rosters of same team), we don't want to remove them
                async with db.execute("""SELECT p.registration_id FROM tournament_players p
                                    JOIN team_squad_registrations s ON p.registration_id = s.registration_id
                                    JOIN tournaments t ON p.tournament_id = t.id
                                    WHERE p.player_id = ? AND s.roster_id = ?
                                    AND (t.date_end > ? OR t.registrations_open = ?) AND t.team_members_only = ?
                                    AND p.is_bagger_clause = ?""",
                                    (player_id, roster_id, curr_time, True, True, is_bagger_clause)) as cursor:
                    rows = await cursor.fetchall()
                    for row in rows:
                        if row[0] in registration_ids:
                            registration_ids.remove(row[0])
                # finally remove the player from all the tournaments they shouldn't be in
                await db.execute(f"DELETE FROM tournament_players WHERE player_id = ? AND registration_id IN ({','.join(map(str, registration_ids))})", (player_id,))

            # next we want to automatically add the transferred player to any team tournaments where that team is registered
            # and registrations are open
            async with db.execute("""SELECT s.registration_id, t.id FROM team_squad_registrations s
                                    JOIN tournaments t ON s.tournament_id = t.id
                                    WHERE t.teams_allowed = ? AND t.registrations_open = ?
                                    AND s.roster_id = ? AND NOT EXISTS (
                                        SELECT p.id FROM tournament_players p WHERE p.player_id = ? AND p.registration_id = s.registration_id
                                  )""", (True, True, roster_id, player_id)) as cursor:
                rows = await cursor.fetchall()
                squads: dict[int, int] = {}
                for row in rows:
                    squad, tournament = row
                    squads[tournament] = squad
            # if the player is already in some of these tournaments we don't want to add them again
            tournament_query = ','.join(map(str, squads.keys()))
            async with db.execute(f"SELECT registration_id, tournament_id FROM tournament_players WHERE player_id = ? AND is_bagger_clause = ? AND tournament_id IN ({tournament_query})",
                                  (player_id, is_bagger_clause)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    squad, tournament = row
                    if tournament in squads.keys():
                        del squads[tournament]
            insert_rows = [(player_id, tournament_id, registration_id, False, curr_time, False, None, False, False, None, False, is_bagger_clause,
                            False) for tournament_id, registration_id in squads.items()]
            await db.executemany("""INSERT INTO tournament_players(player_id, tournament_id, registration_id, is_squad_captain, timestamp, is_checked_in, mii_name, can_host, is_invite, selected_fc_id, 
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
            fc_type = game_fc_map[game]
            async with db.execute("SELECT id FROM friend_codes WHERE type = ? AND player_id = ? AND is_active = ?", (fc_type, self.player_id, True)) as cursor:
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
                async with db.execute("""SELECT p.registration_id FROM tournament_players p
                                    JOIN team_squad_registrations s ON p.registration_id = s.registration_id
                                    JOIN tournaments t ON p.tournament_id = t.id
                                    WHERE p.player_id = ? AND s.roster_id = ?
                                    AND (t.date_end > ? OR t.registrations_open = ?) AND t.team_members_only = ?
                                    AND p.is_bagger_clause = ?""",
                                    (self.player_id, self.roster_leave_id, curr_time, True, True, self.is_bagger_clause)) as cursor:
                    rows = await cursor.fetchall()
                    registration_ids: list[int] = [row[0] for row in rows]
                # if any of these squads the player was in previously are also linked to the new roster,
                # (such as when transferring between two rosters of same team), we don't want to remove them
                async with db.execute("""SELECT p.registration_id FROM tournament_players p
                                    JOIN team_squad_registrations s ON p.registration_id = s.registration_id
                                    JOIN tournaments t ON p.tournament_id = t.id
                                    WHERE p.player_id = ? AND s.roster_id = ?
                                    AND (t.date_end > ? OR t.registrations_open = ?) AND t.team_members_only = ?
                                    AND p.is_bagger_clause = ?""",
                                    (self.player_id, self.roster_id, curr_time, True, True, self.is_bagger_clause)) as cursor:
                    rows = await cursor.fetchall()
                    for row in rows:
                        if row[0] in registration_ids:
                            registration_ids.remove(row[0])
                # finally remove the player from all the tournaments they shouldn't be in
                await db.execute(f"DELETE FROM tournament_players WHERE player_id = ? AND registration_id IN ({','.join(map(str, registration_ids))})", (self.player_id,))

            # next we want to automatically add the transferred player to any team tournaments where that team is registered
            # and registrations are open
            async with db.execute("""SELECT s.registration_id, t.id FROM team_squad_registrations s
                                    JOIN tournaments t ON s.tournament_id = t.id
                                    WHERE t.teams_allowed = ? AND t.registrations_open = ?
                                    AND s.roster_id = ? AND NOT EXISTS (
                                        SELECT p.id FROM tournament_players p 
                                        WHERE p.player_id = ? AND p.registration_id = s.registration_id
                                    )""", (True, True, self.roster_id, self.player_id)) as cursor:
                rows = await cursor.fetchall()
                squads: dict[int, int] = {}
                for row in rows:
                    squad, tournament = row
                    squads[tournament] = squad
            # if the player is already in some of these tournaments we don't want to add them again
            tournament_query = ','.join(map(str, squads.keys()))
            async with db.execute(f"SELECT registration_id, tournament_id FROM tournament_players WHERE player_id = ? AND tournament_id IN ({tournament_query})",
                                  (self.player_id,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    squad, tournament = row
                    if tournament in squads.keys():
                        del squads[tournament]
            insert_rows = [(self.player_id, tournament_id, registration_id, False, curr_time, False, None, False, False, None, False, self.is_bagger_clause,
                            False) for tournament_id, registration_id in squads.items()]
            await db.executemany("""INSERT INTO tournament_players(player_id, tournament_id, registration_id, is_squad_captain, timestamp, is_checked_in, mii_name, can_host, is_invite, selected_fc_id, 
                                 is_representative, is_bagger_clause, is_approved)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", insert_rows)
            await db.commit()

@save_to_command_log
@dataclass
class ToggleTeamMemberBaggerCommand(Command[None]):
    roster_id: int
    player_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("""SELECT m.id, m.is_bagger_clause, r.game FROM team_members m
                                  JOIN team_rosters r ON m.roster_id = r.id
                                  WHERE m.roster_id = ? AND m.player_id = ? AND m.leave_date IS ?""",
                                  (self.roster_id, self.player_id, None)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Team member not found", status=404)
                member_id, is_bagger_clause, roster_game = row
                if roster_game != "mkw":
                    raise Problem("Cannot toggle bagger clause for games other than MKW", status=400)
            await db.execute("UPDATE team_members SET is_bagger_clause = ? WHERE id = ?", (not is_bagger_clause, member_id))
            await db.commit()