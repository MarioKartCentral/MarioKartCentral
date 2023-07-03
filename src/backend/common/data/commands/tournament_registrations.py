from dataclasses import dataclass
from datetime import datetime
from typing import List

from common.data.commands import Command, save_to_command_log
from common.data.models import Problem, SquadPlayerDetails, TournamentPlayerDetails, TournamentSquadDetails


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
        timestamp = int(datetime.utcnow().timestamp())
        async with db_wrapper.connect() as db:
            # check if registrations are open and if mii name is required
            async with db.execute("SELECT is_squad, max_squad_size, mii_name_required, registrations_open, team_members_only FROM tournaments WHERE id = ?", (self.tournament_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem("Tournament not found", status=404)
                is_squad, max_squad_size, mii_name_required, registrations_open, team_members_only = row
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
                    
            # check if player exists if we are force-registering them
            if not self.is_privileged:
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
                    WHERE m.player_id = ? AND m.leave_date = ? AND r.squad_id IS ?""",
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
                self.is_invite, self.selected_fc_id, self.is_representative))
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
    is_checked_in: bool
    is_squad_captain: bool
    selected_fc_id: int | None
    is_representative: bool | None
    is_privileged: bool
    
    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT registrations_open, mii_name_required FROM tournaments WHERE tournament_id = ?", (self.tournament_id,)) as cursor:
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
            async with db.execute("SELECT id, is_invite, is_representative FROM tournament_players WHERE tournament_id = ? AND squad_id IS ? AND player_id = ?",
                (self.tournament_id, self.squad_id, self.player_id)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Registration not found", status=404)
                registration_id, curr_is_invite, curr_is_rep = row
            if self.is_representative is None:
                self.is_representative = curr_is_rep
            # if a player accepts an invite while already registered for a different squad, their old registration must be removed
            if curr_is_invite and (not self.is_invite):
                await db.execute("DELETE FROM tournament_players WHERE tournament_id = ? AND player_id = ? AND is_invite = ?",
                    (self.tournament_id, self.player_id, False))
            await db.execute("UPDATE tournament_players SET mii_name = ?, can_host = ?, is_invite = ?, is_checked_in = ?, is_squad_captain = ?, selected_fc_id = ?, is_representative = ? WHERE id = ?", (
                self.mii_name, self.can_host, self.is_invite, self.is_checked_in, self.is_squad_captain, self.selected_fc_id, self.is_representative, registration_id))
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
            async with db.execute("DELETE FROM tournament_players WHERE tournament_id = ? AND squad_id IS ? AND player_id = ?", (self.tournament_id, self.squad_id, self.player_id)) as cursor:
                rowcount = cursor.rowcount
                if rowcount == 0:
                    raise Problem("Registration not found", status=404)
            # we should unregister a squad if it has no members remaining after this player is unregistered
            if self.squad_id is not None:
                async with db.execute("SELECT count(id) FROM tournament_players WHERE tournament_id = ? AND squad_id IS ?", (self.tournament_id, self.squad_id)) as cursor:
                    row = await cursor.fetchone()
                    assert row is not None
                    num_squad_players = row[0]
                if num_squad_players == 0:
                    await db.execute("UPDATE tournament_squads SET is_registered = ? WHERE id = ?", (False, self.squad_id))
            await db.commit()

@dataclass
class GetSquadRegistrationsCommand(Command[List[TournamentSquadDetails]]):
    tournament_id: int
    eligible_only: bool

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            where_clause = ""
            if self.eligible_only:
                where_clause = "AND is_registered = 1"
            async with db.execute(f"SELECT id, name, tag, color, timestamp, is_registered FROM tournament_squads WHERE tournament_id = ? {where_clause}", (self.tournament_id,)) as cursor:
                rows = await cursor.fetchall()
                squads = {}
                for row in rows:
                    squad_id, squad_name, squad_tag, squad_color, squad_timestamp, is_registered = row
                    curr_squad = TournamentSquadDetails(squad_id, squad_name, squad_tag, squad_color, squad_timestamp, is_registered, [])
                    squads[squad_id] = curr_squad
            async with db.execute("""SELECT t.player_id, t.squad_id, t.is_squad_captain, t.timestamp, t.is_checked_in, 
                                    t.mii_name, t.can_host, t.is_invite, t.selected_fc_id,
                                    p.name, p.country_code, p.discord_id
                                    FROM tournament_players t
                                    JOIN players p on t.player_id = p.id
                                    WHERE t.tournament_id = ?""",
                                    (self.tournament_id,)) as cursor:
                rows = await cursor.fetchall()
                player_dict = {} # creating a dictionary of players so we can add their FCs to them later
                fc_id_list = [] # if require_single_fc is true, we will need to know exactly which FCs to retrieve
                for row in rows:
                    player_id, squad_id, is_squad_captain, player_timestamp, is_checked_in, mii_name, can_host, is_invite, selected_fc_id, player_name, country, discord_id = row
                    if squad_id not in squads:
                        continue
                    curr_player = SquadPlayerDetails(player_id, player_timestamp, is_checked_in, mii_name, can_host, player_name, country, discord_id, [], is_squad_captain, is_invite)
                    curr_squad = squads[squad_id]
                    curr_squad.players.append(curr_player)

                    player_dict[player_id] = curr_player
                    fc_id_list.append(selected_fc_id) # Add this FC's ID to the list of FCs we query for if require_single_fc is true for the current tournament
            # check if only single FCs are allowed or not
            async with db.execute("SELECT require_single_fc FROM tournaments WHERE id = ?", (self.tournament_id,)) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                require_single_fc = bool(row[0])
                fc_where_clause = ""
                if require_single_fc:
                    fc_where_clause = f" AND id IN ({','.join(map(str, fc_id_list))})" # convert all FC IDs to str and join with a comma
            # gathering all the valid FCs for each player for this tournament
            fc_query = f"SELECT id, player_id, fc FROM friend_codes WHERE player_id IN ({','.join(map(str, player_dict.keys()))}){fc_where_clause}"
            async with db.execute(fc_query) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    fc_id, player_id, fc = row
                    player_dict[player_id].friend_codes.append(fc)
        return list(squads.values())
    
@dataclass
class GetFFARegistrationsCommand(Command[List[TournamentPlayerDetails]]):
    tournament_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute("""SELECT t.player_id, t.timestamp, t.is_checked_in, t.mii_name, t.can_host, t.selected_fc_id,
                                    p.name, p.country_code, p.discord_id
                                    FROM tournament_players t
                                    JOIN players p on t.player_id = p.id
                                    WHERE t.tournament_id = ?""",
                                    (self.tournament_id,)) as cursor:
                rows = await cursor.fetchall()
                players = []

                player_dict = {} # creating a dictionary of players so we can add their FCs to them later
                fc_id_list = [] # if require_single_fc is true, we will need to know exactly which FCs to retrieve

                for row in rows:
                    player_id, player_timestamp, is_checked_in, mii_name, can_host, selected_fc_id, name, country, discord_id = row
                    curr_player = TournamentPlayerDetails(player_id, player_timestamp, is_checked_in, mii_name, can_host, name, country, discord_id, [])
                    players.append(curr_player)
                    
                    player_dict[player_id] = curr_player
                    fc_id_list.append(selected_fc_id) # Add this FC's ID to the list of FCs we query for if require_single_fc is true for the current tournament

            # check if only single FCs are allowed or not and get the tournament's game
            async with db.execute("SELECT require_single_fc, game FROM tournaments WHERE id = ?", (self.tournament_id,)) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                require_single_fc = bool(row[0])
                game = row[1]
                fc_where_clause = ""
                if require_single_fc:
                    fc_where_clause = f" AND id IN ({','.join(map(str, fc_id_list))})" # convert all FC IDs to str and join with a comma
            # gathering all the valid FCs for each player for this tournament
            fc_query = f"SELECT id, player_id, fc FROM friend_codes WHERE game = ? AND player_id IN ({','.join(map(str, player_dict.keys()))}){fc_where_clause}"
            variable_parameters = (game,)
            async with db.execute(fc_query, variable_parameters) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    fc_id, player_id, fc = row
                    player_dict[player_id].friend_codes.append(fc)
                return players