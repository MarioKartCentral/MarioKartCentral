from dataclasses import dataclass
from datetime import datetime, timezone

from common.data.commands import Command, save_to_command_log
from common.data.models import *


@save_to_command_log
@dataclass
class RegisterPlayerCommand(Command[None]):
    player_id: int
    tournament_id: int
    squad_id: int | None
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
                if bool(is_squad) and self.squad_id is None:
                    raise Problem("Players may not register alone for squad tournaments", status=400)
                if not bool(is_squad) and self.squad_id is not None:
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
            
            # check if squad exists and if we are using the squad's tag in our mii name
            if self.squad_id is not None:
                async with db.execute("SELECT tag FROM tournament_squads WHERE id = ? AND tournament_id = ?", (self.squad_id, self.tournament_id)) as cursor:
                    row = await cursor.fetchone()
                    if row is None:
                        raise Problem("Squad not found", status=404)
                    squad_tag = row[0]
                    if squad_tag is not None and self.mii_name is not None:
                        if squad_tag not in self.mii_name:
                            raise Problem("Mii name must contain squad tag", status=400)
                        
            # make sure the player is in a team roster that is linked to the current squad
            if bool(team_members_only):
                async with db.execute("""SELECT m.id FROM team_members m
                    JOIN team_squad_registrations r ON m.roster_id = r.roster_id
                    WHERE m.player_id = ? AND m.leave_date IS ? AND r.squad_id IS ?""",
                    (self.player_id, None, self.squad_id)) as cursor:
                    row = await cursor.fetchone()
                    if row is None:
                        raise Problem("Player must be registered for a team roster linked to this squad", status=400)
                    
            # check if player has already registered for the tournament
            async with db.execute("SELECT squad_id, is_bagger_clause from tournament_players WHERE player_id = ? AND tournament_id = ? AND is_invite = 0", 
                                  (self.player_id, self.tournament_id)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    existing_squad_id, is_bagger_clause = row
                    # if row exists but existing_squad_id is None, it's a FFA and theyre already registered
                    if not existing_squad_id:
                        raise Problem("Player is already registered for this tournament", status=400)
                    if existing_squad_id == self.squad_id:
                        raise Problem("Player is already invited to/registered for this squad", status=400)
                    # should still be able to invite someone if they are registered for the tournament
                    # if the registered player's bagger clause is the opposite of our current one, let them register
                    if (not self.is_invite) and is_bagger_clause == self.is_bagger_clause:
                        raise Problem('Player is already registered for this tournament', status=400)
                    
            # check if player's squad is at maximum number of players
            if self.squad_id is not None and max_squad_size is not None:
                async with db.execute("SELECT id FROM tournament_players WHERE tournament_id = ? AND squad_id IS ?", (self.tournament_id, self.squad_id)) as cursor:
                    player_squad_size = cursor.rowcount
                    if player_squad_size >= max_squad_size:
                        raise Problem('Squad at maximum number of players', status=400)
                    
            await db.execute("""INSERT INTO tournament_players(player_id, tournament_id, squad_id, is_squad_captain, timestamp, is_checked_in, mii_name, can_host, is_invite, selected_fc_id, 
                             is_representative, is_bagger_clause, is_approved)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (self.player_id, self.tournament_id, self.squad_id, self.is_squad_captain, timestamp, self.is_checked_in, self.mii_name, self.can_host, 
                self.is_invite, selected_fc_id, self.is_representative, self.is_bagger_clause, self.is_approved))
            await db.commit()


@save_to_command_log
@dataclass
class EditPlayerRegistrationCommand(Command[None]):
    tournament_id: int
    squad_id: int | None
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
            async with db.execute("SELECT id, is_invite, is_representative, is_squad_captain, is_checked_in, is_bagger_clause, is_approved FROM tournament_players WHERE tournament_id = ? AND squad_id IS ? AND player_id = ?",
                (self.tournament_id, self.squad_id, self.player_id)) as cursor:
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

            # check if squad exists and if we are using the squad's tag in our mii name
            if self.squad_id is not None:
                async with db.execute("SELECT tag FROM tournament_squads WHERE id = ? AND tournament_id = ?", (self.squad_id, self.tournament_id)) as cursor:
                    row = await cursor.fetchone()
                    if row is None:
                        raise Problem("Squad not found", status=404)
                    squad_tag = row[0]
                    if squad_tag is not None and self.mii_name is not None:
                        if squad_tag not in self.mii_name:
                            raise Problem("Mii name must contain squad tag", status=400)

            # if a player accepts an invite while already registered for a different squad, their old registration must be removed
            if curr_is_invite and (not self.is_invite):
                old_squad_id = None
                old_is_squad_captain = False
                async with db.execute("SELECT squad_id, is_squad_captain FROM tournament_players WHERE tournament_id = ? AND player_id = ? AND is_invite = ?",
                    (self.tournament_id, self.player_id, False)) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        old_squad_id, old_is_squad_captain = row
                
                if old_squad_id:
                    # we should unregister a squad if it has no members remaining after this player is unregistered
                    async with db.execute("SELECT count(*) FROM tournament_players WHERE tournament_id = ? AND squad_id IS ? AND is_invite = 0", (self.tournament_id, old_squad_id)) as cursor:
                        row = await cursor.fetchone()
                        assert row is not None
                        num_squad_players = row[0]
                    # disallow players from leaving their squad as captain if there is more than 1 player
                    if old_is_squad_captain and num_squad_players > 1:
                        raise Problem("Please unregister your current squad or give captain to another player in your squad before leaving your current squad", status=400)
                    if num_squad_players == 1:
                        await db.execute("UPDATE tournament_squads SET is_registered = ? WHERE id = ?", (False, old_squad_id))
                        # delete any invites as well
                        await db.execute("DELETE FROM tournament_players WHERE tournament_id = ? AND squad_id IS ? AND is_invite = 1", (self.tournament_id, old_squad_id))
                    await db.execute("DELETE FROM tournament_players WHERE tournament_id = ? AND player_id = ? AND squad_id = ?",
                        (self.tournament_id, self.player_id, old_squad_id))
                    
            # if we're making this player the captain, make sure no one else is captain
            if is_squad_captain:
                await db.execute("UPDATE tournament_players SET is_squad_captain = ? WHERE tournament_id = ? AND squad_id = ? AND player_id != ?",
                                 (False, self.tournament_id, self.squad_id, self.player_id))
            await db.execute("""UPDATE tournament_players SET mii_name = ?, can_host = ?, is_invite = ?, is_checked_in = ?, is_squad_captain = ?, 
                             selected_fc_id = ?, is_representative = ?, is_bagger_clause = ?, is_approved = ? WHERE id = ?""", (
                self.mii_name, self.can_host, self.is_invite, is_checked_in, is_squad_captain, self.selected_fc_id, is_representative, is_bagger_clause, is_approved, registration_id))
            await db.commit()

@save_to_command_log
@dataclass
class UnregisterPlayerCommand(Command[None]):
    tournament_id: int
    squad_id: int | None
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
            async with db.execute("SELECT is_squad_captain, id FROM tournament_players WHERE tournament_id = ? AND squad_id iS ? AND player_id = ?",
                                  (self.tournament_id, self.squad_id, self.player_id)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Player is not registered for this tournament", status=400)
                is_squad_captain, registration_id = row
            if self.squad_id is not None:
                # we should unregister a squad if it has no members remaining after this player is unregistered
                async with db.execute("SELECT count(*) FROM tournament_players WHERE tournament_id = ? AND squad_id IS ? AND is_invite = 0", (self.tournament_id, self.squad_id)) as cursor:
                    row = await cursor.fetchone()
                    assert row is not None
                    num_squad_players = row[0]
                # disallow players from leaving their squad as captain if there is more than 1 player
                if is_squad_captain and num_squad_players > 1:
                    raise Problem("Please unregister your current squad or give captain to another player in your squad before unregistering for this tournament", status=400)
                if is_squad_captain and num_squad_players == 1:
                    await db.execute("UPDATE tournament_squads SET is_registered = ? WHERE id = ?", (False, self.squad_id))
                    # delete any invites as well
                    await db.execute("DELETE FROM tournament_players WHERE tournament_id = ? AND squad_id IS ? AND is_invite = 1", (self.tournament_id, self.squad_id))
            await db.execute("DELETE FROM tournament_solo_placements WHERE tournament_id = ? AND player_id = ?", (self.tournament_id, registration_id))
            async with db.execute("DELETE FROM tournament_players WHERE tournament_id = ? AND squad_id IS ? AND player_id = ?", (self.tournament_id, self.squad_id, self.player_id)) as cursor:
                rowcount = cursor.rowcount
                if rowcount == 0:
                    raise Problem("Registration not found", status=404)
            await db.commit()

@dataclass
class GetSquadRegistrationsCommand(Command[list[TournamentSquadDetails]]):
    tournament_id: int
    registered_only: bool
    eligible_only: bool
    hosts_only: bool
    is_approved: bool | None

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute("SELECT game, verification_required, checkins_enabled, min_players_checkin, min_squad_size, teams_allowed FROM tournaments WHERE id = ?",
                                  (self.tournament_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Tournament not found", status=400)
                game, verification_required, checkins_enabled, min_players_checkin, min_squad_size, teams_allowed = row
            where_clauses = ["tournament_id = ?"]
            variable_parameters = [self.tournament_id]
            # get only squads which have not withdrawn from the tournament
            if self.registered_only:
                where_clauses.append("is_registered = 1")
            # get only squads which have the minimum number of players
            if self.eligible_only:
                if min_squad_size:
                    where_clauses.append("t.min_squad_size <= (SELECT COUNT(*) FROM tournament_players p WHERE p.tournament_id = s.tournament_id AND p.squad_id = s.id AND p.is_invite = 0)")
                if bool(checkins_enabled) and min_players_checkin is not None:
                    where_clauses.append("t.min_players_checkin <= (SELECT COUNT(*) FROM tournament_players p WHERE p.tournament_id = s.tournament_id AND p.squad_id = s.id AND p.is_invite = 0 AND p.is_checked_in = 1)")
            if self.hosts_only:
                where_clauses.append("EXISTS (SELECT p.id FROM tournament_players p WHERE p.tournament_id = s.tournament_id AND p.squad_id = s.id AND p.can_host = 1)")
            if self.is_approved is not None and bool(verification_required):
                where_clauses.append("s.is_approved = ?")
                variable_parameters.append(self.is_approved)
            where_clause = " AND ".join(where_clauses)
            squads: dict[int, TournamentSquadDetails] = {}
            async with db.execute(f"""SELECT s.id, s.name, s.tag, s.color, s.timestamp, s.is_registered, s.is_approved
                                  FROM tournament_squads s
                                  JOIN tournaments t ON s.tournament_id = t.id
                                  WHERE {where_clause}""", variable_parameters) as cursor:
                rows = await cursor.fetchall()
                
                for row in rows:
                    squad_id, squad_name, squad_tag, squad_color, squad_timestamp, is_registered, is_approved = row
                    curr_squad = TournamentSquadDetails(squad_id, squad_name, squad_tag, squad_color, squad_timestamp, is_registered, is_approved, [], [])
                    squads[squad_id] = curr_squad
            # get teams connected to squads
            if teams_allowed:
                async with db.execute(f"""SELECT tsr.squad_id, tr.id, tr.team_id, tr.name, tr.tag, t.name, t.tag, t.color
                                    FROM team_squad_registrations tsr
                                    JOIN team_rosters tr ON tsr.roster_id = tr.id
                                    JOIN teams t ON tr.team_id = t.id
                                    WHERE tsr.squad_id IN (
                                        SELECT s.id FROM tournament_squads s
                                        JOIN tournaments t ON s.tournament_id = t.id
                                        WHERE {where_clause}
                                    )""", variable_parameters) as cursor:
                    rows = await cursor.fetchall()
                    for row in rows:
                        squad_id, roster_id, team_id, roster_name, roster_tag, team_name, team_tag, team_color = row
                        roster = RosterBasic(team_id, team_name, team_tag, team_color, roster_id, roster_name if roster_name else team_name, roster_tag if roster_tag else team_tag)
                        squad = squads.get(squad_id, None)
                        if squad:
                            squad.rosters.append(roster)
            # get tournament players
            async with db.execute("""SELECT t.id, t.player_id, t.squad_id, t.is_squad_captain, t.is_representative, t.timestamp, t.is_checked_in, 
                                    t.mii_name, t.can_host, t.is_invite, t.selected_fc_id, t.is_bagger_clause, t.is_approved, p.name, p.country_code, 
                                    d.discord_id, d.username, d.discriminator, d.global_name, d.avatar
                                    FROM tournament_players t
                                    JOIN players p on t.player_id = p.id
                                    LEFT JOIN users u ON u.player_id = p.id
                                    LEFT JOIN user_discords d ON u.id = d.user_id
                                    WHERE t.tournament_id = ?""",
                                    (self.tournament_id,)) as cursor:
                rows = await cursor.fetchall()
                player_fc_dict: dict[int, list[FriendCode]] = {} # create a dictionary of player fcs so we can give all players their FCs
                for row in rows:
                    (reg_id, player_id, squad_id, is_squad_captain, is_representative, player_timestamp, is_checked_in, mii_name, can_host, is_invite, selected_fc_id, 
                     is_bagger_clause, is_approved, player_name, country, 
                     discord_id, d_username, d_discriminator, d_global_name, d_avatar) = row
                    if squad_id not in squads:
                        continue
                    player_discord = None
                    if discord_id:
                        player_discord = Discord(discord_id, d_username, d_discriminator, d_global_name, d_avatar)
                    curr_player = SquadPlayerDetails(reg_id, player_id, squad_id, player_timestamp, is_checked_in, is_approved, mii_name, can_host, player_name, country, player_discord, selected_fc_id, [], is_squad_captain, 
                                                     is_representative, is_invite, is_bagger_clause)
                    curr_squad = squads[squad_id]
                    curr_squad.players.append(curr_player)
                    player_fc_dict[player_id] = []
            # gathering all the valid FCs for each player for this tournament
            fc_query = f"""SELECT id, player_id, game, fc, is_verified, is_primary, description, is_active FROM friend_codes f WHERE f.game = ? AND player_id IN (
                            SELECT t.player_id FROM tournament_players t WHERE t.tournament_id = ?
                        )"""
            async with db.execute(fc_query, (game, self.tournament_id)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    fc_id, player_id, game, fc, is_verified, is_primary, description, is_active = row
                    if player_id not in player_fc_dict:
                        continue
                    player_fc_dict[player_id].append(FriendCode(fc_id, fc, game, player_id, bool(is_verified), bool(is_primary), description, bool(is_active)))
            # finally, set all players' friend codes.
            # we need to do this at the end because some players might have two registration entries
            # (ex. if a player is invited to two different squads), so we need to make sure both of their
            # registrations have all their friend codes attached.
            for squad in squads.values():
                for player in squad.players:
                    player.friend_codes = player_fc_dict[player.player_id]
        return list(squads.values())
    
@dataclass
class GetFFARegistrationsCommand(Command[list[TournamentPlayerDetails]]):
    tournament_id: int
    eligible_only: bool
    hosts_only: bool
    is_approved: bool | None

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute("SELECT game, verification_required, checkins_enabled FROM tournaments WHERE id = ?", (self.tournament_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Tournament not found", status=400)
                game, verification_required, checkins_enabled = row
            where_clauses = ["t.tournament_id = ?"]
            variable_parameters = [self.tournament_id]
            if self.eligible_only and bool(checkins_enabled):
                where_clauses.append("t.is_checked_in = 1")
            if self.hosts_only:
                where_clauses.append("t.can_host = 1")
            if self.is_approved is not None and bool(verification_required):
                where_clauses.append("t.is_approved = ?")
                variable_parameters.append(self.is_approved)
            where_clause = " AND ".join(where_clauses)
            async with db.execute(f"""SELECT t.id, t.player_id, t.timestamp, t.is_checked_in, t.mii_name, t.can_host, t.selected_fc_id, t.is_approved, p.name, p.country_code, 
                                    d.discord_id, d.username, d.discriminator, d.global_name, d.avatar
                                    FROM tournament_players t
                                    JOIN players p on t.player_id = p.id
                                    LEFT JOIN users u ON u.player_id = p.id
                                    LEFT JOIN user_discords d ON u.id = d.user_id
                                    WHERE {where_clause}""",
                                    variable_parameters) as cursor:
                rows = await cursor.fetchall()
                players: list[TournamentPlayerDetails] = []

                player_dict: dict[int, TournamentPlayerDetails] = {} # creating a dictionary of players so we can add their FCs to them later

                for row in rows:
                    (reg_id, player_id, player_timestamp, is_checked_in, mii_name, can_host, selected_fc_id, is_approved, name, country, 
                     discord_id, d_username, d_discriminator, d_global_name, d_avatar) = row
                    player_discord = None
                    if discord_id:
                        player_discord = Discord(discord_id, d_username, d_discriminator, d_global_name, d_avatar)
                    curr_player = TournamentPlayerDetails(reg_id, player_id, None, player_timestamp, is_checked_in, is_approved, mii_name, can_host, name, country, player_discord, selected_fc_id, [])
                    players.append(curr_player)
                    
                    player_dict[player_id] = curr_player

            # gathering all the valid FCs for each player for this tournament
            fc_query = f"""SELECT id, player_id, game, fc, is_verified, is_primary, description, is_active FROM friend_codes f WHERE f.game = ? AND player_id IN (
                            SELECT t.player_id FROM tournament_players t WHERE {where_clause}
                        )
                        """
            async with db.execute(fc_query, (game, *variable_parameters)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    fc_id, player_id, game, fc, is_verified, is_primary, description, is_active = row
                    player_dict[player_id].friend_codes.append(FriendCode(fc_id, fc, game, player_id, bool(is_verified), bool(is_primary), description, bool(is_active)))
                return players
            
@dataclass
class GetPlayerSquadRegCommand(Command[MyTournamentRegistrationDetails]):
    tournament_id: int
    player_id: int
    
    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute("SELECT game, teams_allowed FROM tournaments WHERE id = ?", (self.tournament_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Tournament not found", status=400)
                game, teams_allowed = row
            # get squads that the player is either in or has been invited to
            async with db.execute(f"""SELECT id, name, tag, color, timestamp, is_registered, is_approved FROM tournament_squads s
                                  WHERE s.tournament_id = ? AND EXISTS (
                                    SELECT p.id FROM tournament_players p
                                    WHERE p.squad_id = s.id AND p.player_id = ?
                                  )
                                """, (self.tournament_id, self.player_id)) as cursor:
                rows = await cursor.fetchall()
                squads: dict[int, TournamentSquadDetails] = {}
                for row in rows:
                    squad_id, squad_name, squad_tag, squad_color, squad_timestamp, is_registered, is_approved = row
                    curr_squad = TournamentSquadDetails(squad_id, squad_name, squad_tag, squad_color, squad_timestamp, is_registered, is_approved, [], [])
                    squads[squad_id] = curr_squad

            # get teams connected to squads
            if teams_allowed:
                async with db.execute(f"""SELECT tsr.squad_id, tr.id, tr.team_id, tr.name, tr.tag, t.name, t.tag, t.color
                                    FROM team_squad_registrations tsr
                                    JOIN team_rosters tr ON tsr.roster_id = tr.id
                                    JOIN teams t ON tr.team_id = t.id
                                    WHERE tsr.squad_id IN (
                                        SELECT s.id FROM tournament_squads s
                                        WHERE s.tournament_id = ? AND EXISTS (
                                            SELECT p.id FROM tournament_players p
                                            WHERE p.squad_id = s.id AND p.player_id = ?
                                        )
                                    )""", (self.tournament_id, self.player_id)) as cursor:
                    rows = await cursor.fetchall()
                    for row in rows:
                        squad_id, roster_id, team_id, roster_name, roster_tag, team_name, team_tag, team_color = row
                        roster = RosterBasic(team_id, team_name, team_tag, team_color, roster_id, roster_name if roster_name else team_name, roster_tag if roster_tag else team_tag)
                        squad = squads.get(squad_id, None)
                        if squad:
                            squad.rosters.append(roster)

            # get all players from squads that the requested player is in
            async with db.execute(f"""SELECT t.id, t.player_id, t.squad_id, t.is_squad_captain, t.is_representative, t.timestamp, t.is_checked_in, 
                                    t.mii_name, t.can_host, t.is_invite, t.selected_fc_id, t.is_bagger_clause, t.is_approved, p.name, p.country_code, 
                                    d.discord_id, d.username, d.discriminator, d.global_name, d.avatar
                                    FROM tournament_players t
                                    JOIN players p on t.player_id = p.id
                                    LEFT JOIN users u ON u.player_id = p.id
                                    LEFT JOIN user_discords d ON u.id = d.user_id
                                    WHERE t.tournament_id = ?
                                    AND EXISTS (
                                        SELECT p2.id FROM tournament_players p2
                                        WHERE p2.squad_id = t.squad_id AND p2.player_id = ?
                                    )
                                    """, (self.tournament_id, self.player_id)) as cursor:
                rows = await cursor.fetchall()
                player_fc_dict: dict[int, list[FriendCode]] = {} # create a dictionary of player fcs so we can give all players their FCs
                for row in rows:
                    (reg_id, player_id, squad_id, is_squad_captain, is_representative, player_timestamp, is_checked_in, mii_name, can_host, 
                     is_invite, selected_fc_id, is_bagger_clause, is_approved, player_name, country, 
                     discord_id, d_username, d_discriminator, d_global_name, d_avatar) = row
                    if squad_id not in squads:
                        continue
                    player_discord = None
                    if discord_id:
                        player_discord = Discord(discord_id, d_username, d_discriminator, d_global_name, d_avatar)
                    curr_player = SquadPlayerDetails(reg_id, player_id, squad_id, player_timestamp, is_checked_in, is_approved,
                                                     mii_name, can_host, player_name, country, player_discord, selected_fc_id, [], is_squad_captain,
                                                     is_representative, is_invite, is_bagger_clause)
                    curr_squad = squads[squad_id]
                    curr_squad.players.append(curr_player)
                    player_fc_dict[player_id] = []

            # gathering all the valid FCs for each player in their squads
            fc_query = f"""SELECT id, player_id, game, fc, is_verified, is_primary, description, is_active FROM friend_codes f WHERE f.game = ? AND player_id IN (
                            SELECT t.player_id FROM tournament_players t WHERE t.tournament_id = ? AND t.squad_id IN (
                                SELECT p2.squad_id FROM tournament_players p2
                                WHERE p2.player_id = ?
                            )
                        )"""
            async with db.execute(fc_query, (game, self.tournament_id, self.player_id)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    fc_id, player_id, game, fc, is_verified, is_primary, description, is_active = row
                    player_fc_dict[player_id].append(FriendCode(fc_id, fc, game, player_id, bool(is_verified), bool(is_primary), description,
                                                                bool(is_active)))

            details = MyTournamentRegistrationDetails(self.player_id, self.tournament_id, [])
            # finally, set all players' friend codes.
            # we need to do this at the end because some players might have two registration entries
            # (ex. if a player is invited to two different squads), so we need to make sure both of their
            # registrations have all their friend codes attached.
            for squad in squads.values():
                for player in squad.players:
                    player.friend_codes = player_fc_dict[player.player_id]
                    if player.player_id == self.player_id:
                        details.registrations.append(MyTournamentRegistration(squad, player))
        return details
    
@dataclass
class GetPlayerSoloRegCommand(Command[MyTournamentRegistrationDetails]):
    tournament_id: int
    player_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute("SELECT game FROM tournaments WHERE id = ?", (self.tournament_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Tournament not found", status=400)
                game = row[0]
            async with db.execute("""SELECT t.id, t.player_id, t.timestamp, t.is_checked_in, t.mii_name, t.can_host, t.selected_fc_id, t.is_approved,
                                    p.name, p.country_code, 
                                    d.discord_id, d.username, d.discriminator, d.global_name, d.avatar
                                    FROM tournament_players t
                                    JOIN players p on t.player_id = p.id
                                    LEFT JOIN users u ON u.player_id = p.id
                                    LEFT JOIN user_discords d ON u.id = d.user_id
                                    WHERE t.tournament_id = ? AND t.player_id = ?""",
                                    (self.tournament_id, self.player_id)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    return MyTournamentRegistrationDetails(self.player_id, self.tournament_id, [])
                
                (reg_id, player_id, player_timestamp, is_checked_in, mii_name, can_host, selected_fc_id, is_approved, name, country, 
                 discord_id, d_username, d_discriminator, d_global_name, d_avatar) = row
                player_discord = None
                if discord_id:
                    player_discord = Discord(discord_id, d_username, d_discriminator, d_global_name, d_avatar)
                player = TournamentPlayerDetails(reg_id, player_id, None, player_timestamp, is_checked_in, is_approved, mii_name, can_host, name, country, player_discord, selected_fc_id, [])

            # gathering all the valid FCs for each player for this tournament
            fc_query = f"""SELECT id, player_id, game, fc, is_verified, is_primary, description, is_active FROM friend_codes f WHERE f.game = ? AND player_id IN (
                            SELECT t.player_id FROM tournament_players t WHERE t.tournament_id = ? AND t.player_id = ?
                        )
                        """
            async with db.execute(fc_query, (game, self.tournament_id, self.player_id)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    fc_id, player_id, game, fc, is_verified, is_primary, description, is_active = row
                    player.friend_codes.append(FriendCode(fc_id, fc, game, player_id, bool(is_verified), bool(is_primary), description, bool(is_active)))
            registration = MyTournamentRegistration(None, player)
            details = MyTournamentRegistrationDetails(self.player_id, self.tournament_id, [registration])
            return details

@dataclass
class TogglePlayerCheckinCommand(Command[None]):
    tournament_id: int
    squad_id: int | None
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
            async with db.execute("SELECT is_checked_in FROM tournament_players where tournament_id = ? AND squad_id IS ? AND player_id = ?",
                                  (self.tournament_id, self.squad_id, self.player_id)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Player not registered for tournament", status=400)
                is_checked_in = bool(row[0])
            await db.execute("UPDATE tournament_players SET is_checked_in = ? WHERE tournament_id = ? AND squad_id IS ? AND player_id = ?",
                                  (not is_checked_in, self.tournament_id, self.squad_id, self.player_id))
            await db.commit()