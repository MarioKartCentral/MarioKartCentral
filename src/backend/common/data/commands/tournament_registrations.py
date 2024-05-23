from dataclasses import dataclass
from datetime import datetime, timezone

from common.data.commands import Command, save_to_command_log
from common.data.models import Problem, SquadPlayerDetails, TournamentPlayerDetails, TournamentSquadDetails, MyTournamentRegistrationDetails


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
    is_privileged: bool #if True, bypasses check for tournament registrations being open

    async def handle(self, db_wrapper, s3_wrapper) -> None:
        timestamp = int(datetime.now(timezone.utc).timestamp())
        async with db_wrapper.connect() as db:
            # check if registrations are open and if mii name is required
            async with db.execute("SELECT is_squad, max_squad_size, mii_name_required, registrations_open, team_members_only, require_single_fc FROM tournaments WHERE id = ?", (self.tournament_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem("Tournament not found", status=404)
                is_squad, max_squad_size, mii_name_required, registrations_open, team_members_only, require_single_fc = row
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
            async with db.execute("SELECT squad_id from tournament_players WHERE player_id = ? AND tournament_id = ? AND is_invite = 0", (self.player_id, self.tournament_id)) as cursor:
                row = await cursor.fetchone()
                existing_squad_id = None
                if row:
                    existing_squad_id = row[0]
                    # if row exists but existing_squad_id is None, it's a FFA and theyre already registered
                    if not existing_squad_id:
                        raise Problem("Player already registered for tournament", status=400)
            if existing_squad_id:
                if existing_squad_id == self.squad_id:
                    raise Problem("Player is already invited to/registered for this squad", status=400)
                # make sure player's squad isn't withdrawn before giving error
                async with db.execute("SELECT is_registered FROM tournament_squads WHERE id IS ?", (existing_squad_id,)) as cursor:
                    row = await cursor.fetchone()
                    assert row is not None
                    is_registered = row[0]
                    if is_registered == 1 and (not self.is_invite): # should still be able to invite someone if they are registered for the tournament
                        raise Problem('Player is already registered for this tournament', status=400)
                    
            # check if player's squad is at maximum number of players
            if self.squad_id is not None and max_squad_size is not None:
                async with db.execute("SELECT id FROM tournament_players WHERE tournament_id = ? AND squad_id IS ?", (self.tournament_id, self.squad_id)) as cursor:
                    player_squad_size = cursor.rowcount
                    if player_squad_size >= max_squad_size:
                        raise Problem('Squad at maximum number of players', status=400)
                    
            await db.execute("""INSERT INTO tournament_players(player_id, tournament_id, squad_id, is_squad_captain, timestamp, is_checked_in, mii_name, can_host, is_invite, selected_fc_id, is_representative)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (self.player_id, self.tournament_id, self.squad_id, self.is_squad_captain, timestamp, self.is_checked_in, self.mii_name, self.can_host, 
                self.is_invite, selected_fc_id, self.is_representative))
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
    is_privileged: bool
    
    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT registrations_open, mii_name_required FROM tournaments WHERE id = ?", (self.tournament_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem('Tournament not found', status=404)
                registrations_open, mii_name_required = row
                # make sure players can't edit their registration details after registrations have closed
                if (not self.is_privileged) and (not registrations_open):
                    raise Problem("Registrations are closed, so you cannot edit your registration details", status=400)
                # check for validity of mii name field
                if (not self.is_invite):
                    if mii_name_required == 1 and self.mii_name is None:
                        raise Problem("Tournament requires a Mii Name", status=400)
                    if mii_name_required == 0 and self.mii_name:
                        raise Problem("Tournament should not have a Mii Name", status=400)
                    
            #check if registration exists
            async with db.execute("SELECT id, is_invite, is_representative, is_squad_captain, is_checked_in FROM tournament_players WHERE tournament_id = ? AND squad_id IS ? AND player_id = ?",
                (self.tournament_id, self.squad_id, self.player_id)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Registration not found", status=404)
                registration_id, curr_is_invite, curr_is_rep, curr_squad_captain, curr_is_checked_in = row

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
            await db.execute("UPDATE tournament_players SET mii_name = ?, can_host = ?, is_invite = ?, is_checked_in = ?, is_squad_captain = ?, selected_fc_id = ?, is_representative = ? WHERE id = ?", (
                self.mii_name, self.can_host, self.is_invite, is_checked_in, is_squad_captain, self.selected_fc_id, is_representative, registration_id))
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
            async with db.execute("SELECT is_squad_captain FROM tournament_players WHERE tournament_id = ? AND squad_id iS ? AND player_id = ?",
                                  (self.tournament_id, self.squad_id, self.player_id)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Player is not registered for this tournament", status=400)
                is_squad_captain = row[0]
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

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            where_clauses = ["tournament_id = ?"]
            variable_parameters = [self.tournament_id]
            # get only squads which have not withdrawn from the tournament
            if self.registered_only:
                where_clauses.append("is_registered = 1")
            # get only squads which have the minimum number of players
            if self.eligible_only:
                where_clauses.append("t.min_squad_size <= (SELECT COUNT(*) FROM tournament_players p WHERE p.tournament_id = s.tournament_id AND p.squad_id = s.id AND p.is_invite = 0)")
            if self.hosts_only:
                where_clauses.append("EXISTS (SELECT p.id FROM tournament_players p WHERE p.tournament_id = s.tournament_id AND p.squad_id = s.id AND p.can_host = 1)")
            where_clause = " AND ".join(where_clauses)
            async with db.execute(f"""SELECT s.id, s.name, s.tag, s.color, s.timestamp, s.is_registered 
                                  FROM tournament_squads s
                                  JOIN tournaments t ON s.tournament_id = t.id
                                  WHERE {where_clause}""", variable_parameters) as cursor:
                rows = await cursor.fetchall()
                squads: dict[int, TournamentSquadDetails] = {}
                for row in rows:
                    squad_id, squad_name, squad_tag, squad_color, squad_timestamp, is_registered = row
                    curr_squad = TournamentSquadDetails(squad_id, squad_name, squad_tag, squad_color, squad_timestamp, is_registered, [])
                    squads[squad_id] = curr_squad
            async with db.execute("""SELECT t.id, t.player_id, t.squad_id, t.is_squad_captain, t.timestamp, t.is_checked_in, 
                                    t.mii_name, t.can_host, t.is_invite, p.name, p.country_code, p.discord_id
                                    FROM tournament_players t
                                    JOIN players p on t.player_id = p.id
                                    WHERE t.tournament_id = ?""",
                                    (self.tournament_id,)) as cursor:
                rows = await cursor.fetchall()
                player_fc_dict: dict[int, list[str]] = {} # create a dictionary of player fcs so we can give all players their FCs
                for row in rows:
                    reg_id, player_id, squad_id, is_squad_captain, player_timestamp, is_checked_in, mii_name, can_host, is_invite, player_name, country, discord_id = row
                    if squad_id not in squads:
                        continue
                    curr_player = SquadPlayerDetails(reg_id, player_id, squad_id, player_timestamp, is_checked_in, mii_name, can_host, player_name, country, discord_id, [], is_squad_captain, is_invite)
                    curr_squad = squads[squad_id]
                    curr_squad.players.append(curr_player)
                    player_fc_dict[player_id] = []
            # check if only single FCs are allowed or not
            async with db.execute("SELECT require_single_fc, game FROM tournaments WHERE id = ?", (self.tournament_id,)) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                require_single_fc, game = row
                fc_where_clause = ""
                if require_single_fc:
                    fc_where_clause = "AND f.id = t.selected_fc_id"
            # gathering all the valid FCs for each player for this tournament
            fc_query = f"""SELECT player_id, fc FROM friend_codes f WHERE f.game = ? AND EXISTS (
                            SELECT t.id FROM tournament_players t WHERE t.tournament_id = ? AND t.player_id = f.player_id {fc_where_clause}
                        )"""
            async with db.execute(fc_query, (game, self.tournament_id)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    player_id, fc = row
                    if player_id not in player_fc_dict:
                        continue
                    player_fc_dict[player_id].append(fc)
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
    hosts_only: bool

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            where_clauses = ["t.tournament_id = ?"]
            variable_parameters = [self.tournament_id]
            if self.hosts_only:
                where_clauses.append("t.can_host = 1")
            where_clause = " AND ".join(where_clauses)
            async with db.execute(f"""SELECT t.id, t.player_id, t.timestamp, t.is_checked_in, t.mii_name, t.can_host, p.name, p.country_code, p.discord_id
                                    FROM tournament_players t
                                    JOIN players p on t.player_id = p.id
                                    WHERE {where_clause}""",
                                    variable_parameters) as cursor:
                rows = await cursor.fetchall()
                players: list[TournamentPlayerDetails] = []

                player_dict: dict[int, TournamentPlayerDetails] = {} # creating a dictionary of players so we can add their FCs to them later

                for row in rows:
                    reg_id, player_id, player_timestamp, is_checked_in, mii_name, can_host, name, country, discord_id = row
                    curr_player = TournamentPlayerDetails(reg_id, player_id, None, player_timestamp, is_checked_in, mii_name, can_host, name, country, discord_id, [])
                    players.append(curr_player)
                    
                    player_dict[player_id] = curr_player

            # check if only single FCs are allowed or not and get the tournament's game
            async with db.execute("SELECT require_single_fc, game FROM tournaments WHERE id = ?", (self.tournament_id,)) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                require_single_fc, game = row
                fc_where_clause = ""
                if require_single_fc:
                    fc_where_clause = "AND f.id = t.selected_fc_id"
            # gathering all the valid FCs for each player for this tournament
            fc_query = f"""SELECT player_id, fc FROM friend_codes f WHERE f.game = ? AND EXISTS (
                            SELECT t.id FROM tournament_players t WHERE {where_clause} AND t.player_id = f.player_id {fc_where_clause}
                        )
                        """
            async with db.execute(fc_query, (game, *variable_parameters)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    player_id, fc = row
                    player_dict[player_id].friend_codes.append(fc)
                return players
            
@dataclass
class GetPlayerSquadRegCommand(Command[MyTournamentRegistrationDetails]):
    tournament_id: int
    player_id: int
    
    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            # get squads that the player is either in or has been invited to
            async with db.execute(f"""SELECT id, name, tag, color, timestamp, is_registered FROM tournament_squads s
                                  WHERE s.tournament_id = ? AND EXISTS (
                                    SELECT p.id FROM tournament_players p
                                    WHERE p.squad_id = s.id AND p.player_id = ?
                                  )
                                """, (self.tournament_id, self.player_id)) as cursor:
                rows = await cursor.fetchall()
                squads: dict[int, TournamentSquadDetails] = {}
                for row in rows:
                    squad_id, squad_name, squad_tag, squad_color, squad_timestamp, is_registered = row
                    curr_squad = TournamentSquadDetails(squad_id, squad_name, squad_tag, squad_color, squad_timestamp, is_registered, [])
                    squads[squad_id] = curr_squad
            # get all players from squads that the requested player is in
            async with db.execute(f"""SELECT t.id, t.player_id, t.squad_id, t.is_squad_captain, t.timestamp, t.is_checked_in, 
                                    t.mii_name, t.can_host, t.is_invite, p.name, p.country_code, p.discord_id
                                    FROM tournament_players t
                                    JOIN players p on t.player_id = p.id
                                    WHERE t.tournament_id = ?
                                    AND EXISTS (
                                        SELECT p2.id FROM tournament_players p2
                                        WHERE p2.squad_id = t.squad_id AND p2.player_id = ?
                                    )
                                    """, (self.tournament_id, self.player_id)) as cursor:
                rows = await cursor.fetchall()
                player_fc_dict: dict[int, list[str]] = {} # create a dictionary of player fcs so we can give all players their FCs
                for row in rows:
                    reg_id, player_id, squad_id, is_squad_captain, player_timestamp, is_checked_in, mii_name, can_host, is_invite, player_name, country, discord_id = row
                    if squad_id not in squads:
                        continue
                    curr_player = SquadPlayerDetails(reg_id, player_id, squad_id, player_timestamp, is_checked_in, mii_name, can_host, player_name, country, discord_id, [], is_squad_captain, is_invite)
                    curr_squad = squads[squad_id]
                    curr_squad.players.append(curr_player)
                    player_fc_dict[player_id] = []

            # check if only single FCs are allowed or not and get the tournament's game
            async with db.execute("SELECT require_single_fc, game FROM tournaments WHERE id = ?", (self.tournament_id,)) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                require_single_fc, game = row
                fc_where_clause = ""
                if require_single_fc:
                    fc_where_clause = "AND (f.id = t.selected_fc_id OR t.is_invite = 1)"

            # gathering all the valid FCs for each player in their squads
            fc_query = f"""SELECT f.player_id, f.fc FROM friend_codes f WHERE f.game = ? AND EXISTS (
                            SELECT t.id FROM tournament_players t WHERE t.tournament_id = ? AND t.player_id = f.player_id {fc_where_clause}
                            AND EXISTS (
                                SELECT p2.id FROM tournament_players p2
                                WHERE p2.squad_id = t.squad_id AND p2.player_id = ?
                            )
                        )"""
            print(fc_query)
            async with db.execute(fc_query, (game, self.tournament_id, self.player_id)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    player_id, fc = row
                    print(fc)
                    player_fc_dict[player_id].append(fc)

            details = MyTournamentRegistrationDetails(self.player_id, self.tournament_id, list(squads.values()), None)
            # finally, set all players' friend codes.
            # we need to do this at the end because some players might have two registration entries
            # (ex. if a player is invited to two different squads), so we need to make sure both of their
            # registrations have all their friend codes attached.
            for squad in squads.values():
                for player in squad.players:
                    player.friend_codes = player_fc_dict[player.player_id]
                    if player.player_id == self.player_id and not player.is_invite:
                        details.player = player

        return details
    
@dataclass
class GetPlayerSoloRegCommand(Command[MyTournamentRegistrationDetails]):
    tournament_id: int
    player_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute("""SELECT t.id, t.player_id, t.timestamp, t.is_checked_in, t.mii_name, t.can_host, p.name, p.country_code, p.discord_id
                                    FROM tournament_players t
                                    JOIN players p on t.player_id = p.id
                                    WHERE t.tournament_id = ? AND t.player_id = ?""",
                                    (self.tournament_id, self.player_id)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    return MyTournamentRegistrationDetails(self.player_id, self.tournament_id, [], None)
                
                reg_id, player_id, player_timestamp, is_checked_in, mii_name, can_host, name, country, discord_id = row
                player = TournamentPlayerDetails(reg_id, player_id, None, player_timestamp, is_checked_in, mii_name, can_host, name, country, discord_id, [])

            # check if only single FCs are allowed or not and get the tournament's game
            async with db.execute("SELECT require_single_fc, game FROM tournaments WHERE id = ?", (self.tournament_id,)) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                require_single_fc, game = row
                fc_where_clause = ""
                if require_single_fc:
                    fc_where_clause = "AND f.id = t.selected_fc_id"
            # gathering all the valid FCs for each player for this tournament
            fc_query = f"""SELECT player_id, fc FROM friend_codes f WHERE f.game = ? AND EXISTS (
                            SELECT t.id FROM tournament_players t WHERE t.tournament_id = ? AND t.player_id = ? AND t.player_id = f.player_id
                            {fc_where_clause}
                        )
                        """
            async with db.execute(fc_query, (game, self.tournament_id, self.player_id)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    player_id, fc = row
                    player.friend_codes.append(fc)
            details = MyTournamentRegistrationDetails(self.player_id, self.tournament_id, [], player)
            return details