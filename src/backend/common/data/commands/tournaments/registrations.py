from dataclasses import dataclass
from datetime import datetime, timezone

from common.data.commands import Command, save_to_command_log
from common.data.models import *
from common.auth import team_permissions

@save_to_command_log
@dataclass
class RegisterPlayerCommand(Command[None]):
    player_id: int
    tournament_id: int
    registration_id: int | None
    is_squad_captain: bool
    is_checked_in: bool
    mii_name: str | None
    can_host: bool
    is_invite: bool
    selected_fc_id: int | None
    is_representative: bool
    is_bagger_clause: bool
    is_approved: bool
    is_privileged: bool #if True, bypasses check for tournament registrations being open

    async def handle(self, db_wrapper, s3_wrapper) -> None:
        timestamp = int(datetime.now(timezone.utc).timestamp())
        async with db_wrapper.connect() as db:
            # check if registrations are open and if mii name is required
            async with db.execute("SELECT is_squad, max_squad_size, mii_name_required, registrations_open, team_members_only, require_single_fc, bagger_clause_enabled FROM tournaments WHERE id = ?",
                                  (self.tournament_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem("Tournament not found", status=404)
                is_squad, max_squad_size, mii_name_required, registrations_open, team_members_only, require_single_fc, bagger_clause_enabled = row
                if bool(is_squad) and self.registration_id is None:
                    raise Problem("Players may not register alone for squad tournaments", status=400)
                if not bool(is_squad) and self.registration_id is not None:
                    raise Problem("Players may not register for a squad for solo tournaments", status=400)
                if (not registrations_open) and (not self.is_privileged):
                    raise Problem("Tournament registrations are closed", status=400)
                if (not self.is_invite):
                    if mii_name_required == 1 and self.mii_name is None:
                        raise Problem("Tournament requires a Mii Name", status=400)
                    if mii_name_required == 0 and self.mii_name:
                        raise Problem("Tournament should not have a Mii Name", status=400)
                if require_single_fc and not self.selected_fc_id and not self.is_invite:
                    raise Problem("Please select an FC to use for this tournament", status=400)
                if not is_squad and (self.is_squad_captain or self.is_representative):
                    raise Problem("is_squad_captain and is_representative fields must be false when is_squad is true", status=400)
                if not bagger_clause_enabled and self.is_bagger_clause:
                    raise Problem("Cannot register as bagger when bagger clause is not enabled", status=400)
                selected_fc_id = self.selected_fc_id
                if not require_single_fc:
                    selected_fc_id = None
                    
            # check if player exists if we are force-registering them
            if self.is_privileged:
                async with db.execute("SELECT id FROM players WHERE id = ?", (self.player_id,)) as cursor:
                    row = await cursor.fetchone()
                    if row is None:
                        raise Problem("Player not found", status=404)
            
            registration_id = self.registration_id
            # check if squad exists and if we are using the squad's tag in our mii name
            if registration_id is not None:
                async with db.execute("SELECT tag FROM tournament_registrations WHERE id = ? AND tournament_id = ?", (registration_id, self.tournament_id)) as cursor:
                    row = await cursor.fetchone()
                    if row is None:
                        raise Problem("Squad not found", status=404)
                    squad_tag = row[0]
                    if squad_tag is not None and self.mii_name is not None:
                        if squad_tag not in self.mii_name:
                            raise Problem("Mii name must contain squad tag", status=400)
            else:
                async with db.execute("INSERT INTO tournament_registrations(color, timestamp, tournament_id, is_registered, is_approved) VALUES(?, ?, ?, ?, ?)",
                                      (0, timestamp, self.tournament_id, True, self.is_approved)) as cursor:
                    new_reg_id = cursor.lastrowid
                    assert new_reg_id is not None
                    registration_id = new_reg_id
                        
            # make sure the player is in a team roster that is linked to the current squad
            if bool(team_members_only):
                async with db.execute("""SELECT m.id FROM team_members m
                    JOIN team_squad_registrations r ON m.roster_id = r.roster_id
                    WHERE m.player_id = ? AND m.leave_date IS ? AND r.registration_id IS ?""",
                    (self.player_id, None, self.registration_id)) as cursor:
                    row = await cursor.fetchone()
                    if row is None:
                        raise Problem("Player must be registered for a team roster linked to this squad", status=400)
                    
            # check if player has already registered for the tournament
            async with db.execute("SELECT registration_id, is_bagger_clause from tournament_players WHERE player_id = ? AND tournament_id = ? AND is_invite = 0", 
                                  (self.player_id, self.tournament_id)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    existing_registration_id, is_bagger_clause = row
                    # if row exists but existing_registration_id is None, it's a FFA and theyre already registered
                    if not existing_registration_id:
                        raise Problem("Player is already registered for this tournament", status=400)
                    if existing_registration_id == self.registration_id:
                        raise Problem("Player is already invited to/registered for this squad", status=400)
                    # should still be able to invite someone if they are registered for the tournament
                    # if the registered player's bagger clause is the opposite of our current one, let them register
                    if (not self.is_invite) and is_bagger_clause == self.is_bagger_clause:
                        raise Problem('Player is already registered for this tournament', status=400)
                    
            # check if player's squad is at maximum number of players
            if self.registration_id is not None and max_squad_size is not None:
                async with db.execute("SELECT id FROM tournament_players WHERE tournament_id = ? AND registration_id IS ?", (self.tournament_id, self.registration_id)) as cursor:
                    player_squad_size = cursor.rowcount
                    if player_squad_size >= max_squad_size:
                        raise Problem('Squad at maximum number of players', status=400)
                    
            await db.execute("""INSERT INTO tournament_players(player_id, tournament_id, registration_id, is_squad_captain, timestamp, is_checked_in, mii_name, can_host, is_invite, selected_fc_id, 
                             is_representative, is_bagger_clause, is_approved)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (self.player_id, self.tournament_id, registration_id, self.is_squad_captain, timestamp, self.is_checked_in, self.mii_name, self.can_host, 
                self.is_invite, selected_fc_id, self.is_representative, self.is_bagger_clause, self.is_approved))
            await db.commit()

@save_to_command_log
@dataclass
class EditPlayerRegistrationCommand(Command[None]):
    tournament_id: int
    registration_id: int
    player_id: int
    mii_name: str | None
    can_host: bool
    is_invite: bool
    is_checked_in: bool | None
    is_squad_captain: bool | None
    selected_fc_id: int | None
    is_representative: bool | None
    is_bagger_clause: bool | None
    is_approved: bool | None
    is_privileged: bool
    
    async def handle(self, db_wrapper, s3_wrapper) -> None:
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT is_squad, mii_name_required, registrations_open, require_single_fc, bagger_clause_enabled FROM tournaments WHERE id = ?", 
                                  (self.tournament_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem('Tournament not found', status=404)
                is_squad, mii_name_required, registrations_open, require_single_fc, bagger_clause_enabled = row
                # make sure players can't edit their registration details after registrations have closed
                if (not self.is_privileged) and (not registrations_open):
                    raise Problem("Registrations are closed, so you cannot edit your registration details", status=400)
                # check for validity of mii name field
                if (not self.is_invite):
                    if mii_name_required == 1 and self.mii_name is None:
                        raise Problem("Tournament requires a Mii Name", status=400)
                    if mii_name_required == 0 and self.mii_name:
                        raise Problem("Tournament should not have a Mii Name", status=400)
                if require_single_fc and not self.selected_fc_id and not self.is_invite:
                    raise Problem("Please select an FC to use for this tournament", status=400)
                if not is_squad and (self.is_squad_captain or self.is_representative):
                    raise Problem("is_squad_captain and is_representative fields must be false when is_squad is true", status=400)
                if not bagger_clause_enabled and self.is_bagger_clause:
                    raise Problem("Cannot register as bagger when bagger clause is not enabled", status=400)
                    
            #check if registration exists
            async with db.execute("SELECT id, is_invite, is_representative, is_squad_captain, is_checked_in, is_bagger_clause, is_approved FROM tournament_players WHERE tournament_id = ? AND registration_id IS ? AND player_id = ?",
                (self.tournament_id, self.registration_id, self.player_id)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Registration not found", status=404)
                registration_id, curr_is_invite, curr_is_rep, curr_squad_captain, curr_is_checked_in, curr_bagger_clause, curr_approved = row

            # if we specify None on any of these fields, we don't want to change them
            is_representative = self.is_representative
            if self.is_representative is None:
                is_representative = curr_is_rep
            is_squad_captain = self.is_squad_captain
            if is_squad_captain is None:
                is_squad_captain = curr_squad_captain
            is_checked_in = self.is_checked_in
            if is_checked_in is None:
                is_checked_in = curr_is_checked_in
            is_bagger_clause = self.is_bagger_clause
            if is_bagger_clause is None:
                is_bagger_clause = curr_bagger_clause
            is_approved = self.is_approved
            if is_approved is None:
                is_approved = curr_approved

            async with db.execute("SELECT tag FROM tournament_registrations WHERE id = ? AND tournament_id = ?", (self.registration_id, self.tournament_id)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem("Squad not found", status=404)
                squad_tag = row[0]
                if squad_tag is not None and self.mii_name is not None:
                    if squad_tag not in self.mii_name:
                        raise Problem("Mii name must contain squad tag", status=400)

            # if a player accepts an invite while already registered for a different squad, their old registration must be removed
            if curr_is_invite and (not self.is_invite):
                old_registration_id = None
                old_is_squad_captain = False
                async with db.execute("SELECT registration_id, is_squad_captain FROM tournament_players WHERE tournament_id = ? AND player_id = ? AND is_invite = ?",
                    (self.tournament_id, self.player_id, False)) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        old_registration_id, old_is_squad_captain = row
                
                if old_registration_id:
                    # we should unregister a squad if it has no members remaining after this player is unregistered
                    async with db.execute("SELECT count(*) FROM tournament_players WHERE tournament_id = ? AND registration_id IS ? AND is_invite = 0", (self.tournament_id, old_registration_id)) as cursor:
                        row = await cursor.fetchone()
                        assert row is not None
                        num_squad_players = row[0]
                    # disallow players from leaving their squad as captain if there is more than 1 player
                    if old_is_squad_captain and num_squad_players > 1:
                        raise Problem("Please unregister your current squad or give captain to another player in your squad before leaving your current squad", status=400)
                    if num_squad_players == 1:
                        # delete any invites as well
                        await db.execute("DELETE FROM tournament_players WHERE tournament_id = ? AND registration_id IS ? AND is_invite = 1", (self.tournament_id, self.registration_id))
                        await db.execute("DELETE FROM tournament_placements WHERE registration_id = ?", (self.registration_id,))
                        await db.execute("DELETE FROM team_squad_registrations WHERE registration_id = ?", (self.registration_id,))
                        await db.execute("DELETE FROM tournament_registrations WHERE id = ?", (self.registration_id,))
                    await db.execute("DELETE FROM tournament_players WHERE tournament_id = ? AND player_id = ? AND registration_id = ?",
                        (self.tournament_id, self.player_id, old_registration_id))
                    
            if self.is_approved is not None and not is_squad:
                await db.execute("UPDATE tournament_registrations SET is_approved = ? WHERE id = ?", (self.is_approved, self.registration_id))
            # if we're making this player the captain, make sure no one else is captain
            if is_squad_captain:
                await db.execute("UPDATE tournament_players SET is_squad_captain = ? WHERE tournament_id = ? AND registration_id = ? AND player_id != ?",
                                 (False, self.tournament_id, self.registration_id, self.player_id))
            await db.execute("""UPDATE tournament_players SET mii_name = ?, can_host = ?, is_invite = ?, is_checked_in = ?, is_squad_captain = ?, 
                             selected_fc_id = ?, is_representative = ?, is_bagger_clause = ?, is_approved = ? WHERE id = ?""", (
                self.mii_name, self.can_host, self.is_invite, is_checked_in, is_squad_captain, self.selected_fc_id, is_representative, is_bagger_clause, is_approved, registration_id))
            await db.commit()

@save_to_command_log
@dataclass
class UnregisterPlayerCommand(Command[None]):
    tournament_id: int
    registration_id: int
    player_id: int
    is_privileged: bool

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT registrations_open FROM tournaments WHERE id = ?", (self.tournament_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem('Tournament not found', status=404)
                registrations_open = row[0]
                if (not self.is_privileged) and (not registrations_open):
                    raise Problem("Registrations are closed, so players cannot be unregistered from this tournament", status=400)
            async with db.execute("SELECT is_squad_captain, is_invite FROM tournament_players WHERE tournament_id = ? AND registration_id iS ? AND player_id = ?",
                                  (self.tournament_id, self.registration_id, self.player_id)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Player is not registered for this tournament", status=400)
                is_squad_captain, player_is_invite = row

            # we should unregister a squad if it has no members remaining after this player is unregistered
            async with db.execute("SELECT count(*) FROM tournament_players WHERE tournament_id = ? AND registration_id = ? AND is_invite = 0", (self.tournament_id, self.registration_id)) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                num_squad_players = row[0]
            # disallow players from leaving their squad as captain if there is more than 1 player
            if is_squad_captain and num_squad_players > 1:
                raise Problem("Please unregister your current squad or give captain to another player in your squad before unregistering for this tournament", status=400)
            
            async with db.execute("DELETE FROM tournament_players WHERE tournament_id = ? AND registration_id IS ? AND player_id = ?", (self.tournament_id, self.registration_id, self.player_id)) as cursor:
                rowcount = cursor.rowcount
                if rowcount == 0:
                    raise Problem("Registration not found", status=404)
                
            if num_squad_players == 1 and not player_is_invite:
                # delete any invites as well
                await db.execute("DELETE FROM tournament_players WHERE tournament_id = ? AND registration_id IS ? AND is_invite = 1 AND player_id != ?", (self.tournament_id, self.registration_id, self.player_id))
                await db.execute("DELETE FROM tournament_placements WHERE registration_id = ?", (self.registration_id,))
                await db.execute("DELETE FROM team_squad_registrations WHERE registration_id = ?", (self.registration_id,))
                await db.execute("DELETE FROM tournament_registrations WHERE id = ?", (self.registration_id,))

            await db.commit()

@dataclass
class GetTournamentRegistrationsCommand(Command[list[TournamentSquadDetails]]):
    tournament_id: int
    registered_only: bool
    eligible_only: bool
    hosts_only: bool
    is_approved: bool | None

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute("SELECT is_squad, game, verification_required, checkins_enabled, min_players_checkin, min_squad_size, teams_allowed FROM tournaments WHERE id = ?",
                                  (self.tournament_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Tournament not found", status=400)
                is_squad, game, verification_required, checkins_enabled, min_players_checkin, min_squad_size, teams_allowed = row
            where_clauses = ["tournament_id = ?"]
            variable_parameters = [self.tournament_id]
            # get only squads which have not withdrawn from the tournament
            if self.registered_only:
                where_clauses.append("is_registered = 1")
            
            if self.eligible_only:
                # get squads with the minimum number of players
                if min_squad_size:
                    where_clauses.append("t.min_squad_size <= (SELECT COUNT(*) FROM tournament_players p WHERE p.tournament_id = s.tournament_id AND p.registration_id = s.id AND p.is_invite = 0)")
                # get squads with the minimum number of checked in players
                if bool(checkins_enabled):
                    if not is_squad:
                        where_clauses.append("1 <= (SELECT COUNT(*) FROM tournament_players p WHERE p.tournament_id = s.tournament_id AND p.registration_id = s.id AND p.is_invite = 0 AND p.is_checked_in = 1)")
                    elif min_players_checkin is not None:
                        where_clauses.append("t.min_players_checkin <= (SELECT COUNT(*) FROM tournament_players p WHERE p.tournament_id = s.tournament_id AND p.registration_id = s.id AND p.is_invite = 0 AND p.is_checked_in = 1)")
            if self.hosts_only:
                where_clauses.append("EXISTS (SELECT p.id FROM tournament_players p WHERE p.tournament_id = s.tournament_id AND p.registration_id = s.id AND p.can_host = 1)")
            if self.is_approved is not None and bool(verification_required):
                where_clauses.append("s.is_approved = ?")
                variable_parameters.append(self.is_approved)
            where_clause = " AND ".join(where_clauses)
            squads: dict[int, TournamentSquadDetails] = {}
            async with db.execute(f"""SELECT s.id, s.name, s.tag, s.color, s.timestamp, s.is_registered, s.is_approved
                                  FROM tournament_registrations s
                                  JOIN tournaments t ON s.tournament_id = t.id
                                  WHERE {where_clause}""", variable_parameters) as cursor:
                rows = await cursor.fetchall()
                
                for row in rows:
                    registration_id, squad_name, squad_tag, squad_color, squad_timestamp, is_registered, is_approved = row
                    curr_squad = TournamentSquadDetails(registration_id, squad_name, squad_tag, squad_color, squad_timestamp, is_registered, is_approved, [], [])
                    squads[registration_id] = curr_squad
            # get teams connected to squads
            if teams_allowed:
                async with db.execute(f"""SELECT tsr.registration_id, tr.id, tr.team_id, tr.name, tr.tag, t.name, t.tag, t.color
                                    FROM team_squad_registrations tsr
                                    JOIN team_rosters tr ON tsr.roster_id = tr.id
                                    JOIN teams t ON tr.team_id = t.id
                                    WHERE tsr.registration_id IN (
                                        SELECT s.id FROM tournament_registrations s
                                        JOIN tournaments t ON s.tournament_id = t.id
                                        WHERE {where_clause}
                                    )""", variable_parameters) as cursor:
                    rows = await cursor.fetchall()
                    for row in rows:
                        registration_id, roster_id, team_id, roster_name, roster_tag, team_name, team_tag, team_color = row
                        roster = RosterBasic(team_id, team_name, team_tag, team_color, roster_id, roster_name if roster_name else team_name, roster_tag if roster_tag else team_tag)
                        squad = squads.get(registration_id, None)
                        if squad:
                            squad.rosters.append(roster)
            # get tournament players
            async with db.execute("""SELECT t.id, t.player_id, t.registration_id, t.is_squad_captain, t.is_representative, t.timestamp, t.is_checked_in, 
                                    t.mii_name, t.can_host, t.is_invite, t.selected_fc_id, t.is_bagger_clause, t.is_approved, p.name, p.country_code, 
                                    d.discord_id, d.username, d.discriminator, d.global_name, d.avatar
                                    FROM tournament_players t
                                    JOIN players p on t.player_id = p.id
                                    LEFT JOIN users u ON u.player_id = p.id
                                    LEFT JOIN user_discords d ON u.id = d.user_id
                                    WHERE t.tournament_id = ?
                                    ORDER BY p.name COLLATE NOCASE""",
                                    (self.tournament_id,)) as cursor:
                rows = await cursor.fetchall()
                player_fc_dict: dict[int, list[FriendCode]] = {} # create a dictionary of player fcs so we can give all players their FCs
                for row in rows:
                    (reg_id, player_id, registration_id, is_squad_captain, is_representative, player_timestamp, is_checked_in, mii_name, can_host, is_invite, selected_fc_id, 
                     is_bagger_clause, is_approved, player_name, country, 
                     discord_id, d_username, d_discriminator, d_global_name, d_avatar) = row
                    if registration_id not in squads:
                        continue
                    player_discord = None
                    if discord_id:
                        player_discord = Discord(discord_id, d_username, d_discriminator, d_global_name, d_avatar)
                    curr_player = SquadPlayerDetails(reg_id, player_id, registration_id, player_timestamp, is_checked_in, is_approved, mii_name, can_host, player_name, country, player_discord, selected_fc_id, [], is_squad_captain, 
                                                     is_representative, is_invite, is_bagger_clause)
                    curr_squad = squads[registration_id]
                    curr_squad.players.append(curr_player)
                    player_fc_dict[player_id] = []
            # gathering all the valid FCs for each player for this tournament
            fc_type = game_fc_map[game]
            fc_query = f"""SELECT id, player_id, type, fc, is_verified, is_primary, description, is_active, creation_date FROM friend_codes f WHERE f.type = ? AND player_id IN (
                            SELECT t.player_id FROM tournament_players t WHERE t.tournament_id = ?
                        )"""
            async with db.execute(fc_query, (fc_type, self.tournament_id)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    fc_id, player_id, type, fc, is_verified, is_primary, description, is_active, creation_date = row
                    if player_id not in player_fc_dict:
                        continue
                    player_fc_dict[player_id].append(FriendCode(fc_id, fc, type, player_id, bool(is_verified), bool(is_primary), creation_date, description, bool(is_active)))
            # finally, set all players' friend codes.
            # we need to do this at the end because some players might have two registration entries
            # (ex. if a player is invited to two different squads), so we need to make sure both of their
            # registrations have all their friend codes attached.
            for squad in squads.values():
                for player in squad.players:
                    player.friend_codes = player_fc_dict[player.player_id]
        return list(squads.values())
            
@dataclass
class GetPlayerRegistrationCommand(Command[MyTournamentRegistrationDetails]):
    tournament_id: int
    player_id: int
    
    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute("SELECT game, teams_allowed FROM tournaments WHERE id = ?", (self.tournament_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Tournament not found", status=400)
                game, teams_allowed = row
            details = MyTournamentRegistrationDetails(self.player_id, self.tournament_id, [])
            # in addition to having a matching tournament ID,
            # we also check that we are either a member of the squad,
            # or that we have register tournament permissions for at least one roster connected
            # to the squad.
            where_clause = """WHERE s.tournament_id = ? AND (
                                s.id IN (
                                    SELECT p.registration_id FROM tournament_players p
                                    WHERE p.player_id = ?
                                ) OR s.id IN (
                                    SELECT tsr.registration_id FROM team_squad_registrations tsr
                                    JOIN team_rosters r ON tsr.roster_id = r.id
                                    JOIN teams t ON r.team_id = t.id
                                    JOIN user_team_roles utr ON utr.team_id = t.id
                                    JOIN users u ON utr.user_id = u.id
                                    JOIN team_role_permissions trp ON trp.role_id = utr.role_id
                                    JOIN team_permissions tp ON trp.permission_id = tp.id
                                    WHERE tp.name = ? AND u.player_id = ?
                                )
                            )"""
            variable_parameters = (self.tournament_id, self.player_id, team_permissions.REGISTER_TOURNAMENT, self.player_id)
            # get squads that the player is either in, has been invited to, or has team permissions for
            # is_squad_captain: whether the player is either actually captain of the squad, or they have register tournament permissions
            #   for at least one roster in the squad.
            # is_invite: just checks if the player is invited, it's put in the main registration class for convenience on the frontend
            async with db.execute(f"""SELECT id, name, tag, color, timestamp, is_registered, is_approved,
                                    CASE
                                        WHEN (
                                            s.id IN (
                                                SELECT p.registration_id FROM tournament_players p
                                                WHERE p.player_id = ? AND p.is_squad_captain = 1
                                            )
                                            OR
                                            s.id IN (
                                                SELECT tsr.registration_id FROM team_squad_registrations tsr
                                                JOIN team_rosters r ON tsr.roster_id = r.id
                                                JOIN teams t ON r.team_id = t.id
                                                JOIN user_team_roles utr ON utr.team_id = t.id
                                                JOIN users u ON utr.user_id = u.id
                                                JOIN team_role_permissions trp ON trp.role_id = utr.role_id
                                                JOIN team_permissions tp ON trp.permission_id = tp.id
                                                WHERE tp.name = ? AND u.player_id = ?
                                            )
                                        ) THEN 1 ELSE 0
                                    END AS is_squad_captain,
                                    CASE
                                        WHEN (
                                            s.id IN (
                                                SELECT p.registration_id FROM tournament_players p
                                                WHERE p.player_id = ? AND p.is_invite = 1
                                            )
                                        ) THEN 1 ELSE 0
                                    END as is_invite
                                    FROM tournament_registrations s
                                  {where_clause}""", (self.player_id, team_permissions.REGISTER_TOURNAMENT, self.player_id, self.player_id, *variable_parameters)) as cursor:
                rows = await cursor.fetchall()
                squads: dict[int, TournamentSquadDetails] = {}
                for row in rows:
                    registration_id, squad_name, squad_tag, squad_color, squad_timestamp, is_registered, is_approved, is_squad_captain, is_invite = row
                    curr_squad = TournamentSquadDetails(registration_id, squad_name, squad_tag, squad_color, squad_timestamp, is_registered, is_approved, [], [])
                    squads[registration_id] = curr_squad
                    details.registrations.append(MyTournamentRegistration(curr_squad, None, bool(is_squad_captain), bool(is_invite)))
            # get teams connected to squads
            if teams_allowed:
                async with db.execute(f"""SELECT tsr.registration_id, tr.id, tr.team_id, tr.name, tr.tag, t.name, t.tag, t.color
                                    FROM team_squad_registrations tsr
                                    JOIN team_rosters tr ON tsr.roster_id = tr.id
                                    JOIN teams t ON tr.team_id = t.id
                                    WHERE tsr.registration_id IN (
                                        SELECT s.id FROM tournament_registrations s
                                        {where_clause}
                                    )""", variable_parameters) as cursor:
                    rows = await cursor.fetchall()
                    for row in rows:
                        registration_id, roster_id, team_id, roster_name, roster_tag, team_name, team_tag, team_color = row
                        roster = RosterBasic(team_id, team_name, team_tag, team_color, roster_id, roster_name if roster_name else team_name, roster_tag if roster_tag else team_tag)
                        squad = squads.get(registration_id, None)
                        if squad:
                            squad.rosters.append(roster)

            # get all players from squads that the requested player is in
            async with db.execute(f"""SELECT t.id, t.player_id, t.registration_id, t.is_squad_captain, t.is_representative, t.timestamp, t.is_checked_in, 
                                    t.mii_name, t.can_host, t.is_invite, t.selected_fc_id, t.is_bagger_clause, t.is_approved, p.name, p.country_code, 
                                    d.discord_id, d.username, d.discriminator, d.global_name, d.avatar
                                    FROM tournament_players t
                                    JOIN players p on t.player_id = p.id
                                    LEFT JOIN users u ON u.player_id = p.id
                                    LEFT JOIN user_discords d ON u.id = d.user_id
                                    WHERE t.registration_id IN (
                                        SELECT s.id FROM tournament_registrations s
                                        {where_clause}
                                    )
                                    ORDER BY p.name COLLATE NOCASE""", variable_parameters) as cursor:
                rows = await cursor.fetchall()
                player_fc_dict: dict[int, list[FriendCode]] = {} # create a dictionary of player fcs so we can give all players their FCs
                for row in rows:
                    (reg_id, player_id, registration_id, is_squad_captain, is_representative, player_timestamp, is_checked_in, mii_name, can_host, 
                     is_invite, selected_fc_id, is_bagger_clause, is_approved, player_name, country, 
                     discord_id, d_username, d_discriminator, d_global_name, d_avatar) = row
                    if registration_id not in squads:
                        continue
                    player_discord = None
                    if discord_id:
                        player_discord = Discord(discord_id, d_username, d_discriminator, d_global_name, d_avatar)
                    curr_player = SquadPlayerDetails(reg_id, player_id, registration_id, player_timestamp, is_checked_in, is_approved,
                                                     mii_name, can_host, player_name, country, player_discord, selected_fc_id, [], is_squad_captain,
                                                     is_representative, is_invite, is_bagger_clause)
                    curr_squad = squads[registration_id]
                    curr_squad.players.append(curr_player)
                    player_fc_dict[player_id] = []

            # gathering all the valid FCs for each player in their squads
            fc_type = game_fc_map[game]
            fc_query = f"""SELECT id, player_id, type, fc, is_verified, is_primary, description, is_active, creation_date FROM friend_codes f WHERE f.type = ? AND player_id IN (
                            SELECT t.player_id FROM tournament_players t WHERE t.tournament_id = ? AND t.registration_id IN (
                                SELECT s.id FROM tournament_registrations s
                                {where_clause}
                            )
                        )"""
            async with db.execute(fc_query, (fc_type, self.tournament_id, *variable_parameters)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    fc_id, player_id, type, fc, is_verified, is_primary, description, is_active, creation_date = row
                    player_fc_dict[player_id].append(FriendCode(fc_id, fc, type, player_id, bool(is_verified), bool(is_primary), creation_date, description,
                                                                bool(is_active)))

            # finally, set all players' friend codes.
            # we need to do this at the end because some players might have two registration entries
            # (ex. if a player is invited to two different squads), so we need to make sure both of their
            # registrations have all their friend codes attached.
            # also, if any of the players in a squad match our own player ID, set reg.player to them
            # for ease of access in the frontend
            for reg in details.registrations:
                for player in reg.squad.players:
                    player.friend_codes = player_fc_dict[player.player_id]
                    if player.player_id == self.player_id:
                        reg.player = player
        return details

@dataclass
class TogglePlayerCheckinCommand(Command[None]):
    tournament_id: int
    registration_id: int
    player_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT checkins_enabled, checkins_open FROM tournaments WHERE id = ?",
                                  (self.tournament_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Tournament not found", status=400)
                checkins_enabled, checkins_open = row
                if not checkins_enabled:
                    raise Problem("Checkins are not enabled for this tournament", status=400)
                if not checkins_open:
                    raise Problem("Checkins are not open for this tournament", status=400)
            async with db.execute("SELECT is_checked_in FROM tournament_players where tournament_id = ? AND registration_id IS ? AND player_id = ?",
                                  (self.tournament_id, self.registration_id, self.player_id)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Player not registered for tournament", status=400)
                is_checked_in = bool(row[0])
            await db.execute("UPDATE tournament_players SET is_checked_in = ? WHERE tournament_id = ? AND registration_id IS ? AND player_id = ?",
                                  (not is_checked_in, self.tournament_id, self.registration_id, self.player_id))
            await db.commit()