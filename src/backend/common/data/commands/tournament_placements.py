from dataclasses import dataclass

from common.data.commands import Command, save_to_command_log
from common.data.models import *

@save_to_command_log
@dataclass
class SetPlacementsCommand(Command[None]):
    tournament_id: int
    is_squad: bool
    body: list[TournamentPlacement]
    registrations: list[TournamentPlayerDetails] | list[TournamentSquadDetails]
    

    async def handle(self, db_wrapper, s3_wrapper):
        b = self.body
        registration_dict = {reg.id: reg for reg in self.registrations}
        # sort with DQs at the end
        sorted_placements = sorted(b, key=lambda x: float('inf') if x.placement is None else x.placement)

        # going through placements in order of rank to make sure they fulfill all criteria
        curr_placement = 1
        curr_bound = None
        for i, placement in enumerate(sorted_placements):
            if placement.placement is None:
                if not placement.is_disqualified:
                    raise Problem("Cannot have null placement value when not disqualified", status=400)
                if placement.placement_lower_bound:
                    raise Problem("Placement must be non-null to set lower bound", status=400)
                if placement.placement_description:
                    raise Problem("Cannot have description for null placements", status=400)
            if placement.placement and placement.is_disqualified:
                raise Problem("Cannot have a placement value while disqualified", status=400)
            if placement.registration_id not in registration_dict.keys():
                raise Problem(f"Registration ID {placement.registration_id} not found in tournament", status=400)
            # if the current placement is not equal to its sorted position in the list or is not tied with the previous placement
            if placement.placement is not None and placement.placement != i+1 and placement.placement != curr_placement:
                raise Problem(f"Error processing placements: Placement for ID {placement.registration_id} has value {placement.placement} instead of {i+1} or {curr_placement}", status=400)
            if i > 0 and placement.placement == curr_placement and placement.placement_lower_bound != curr_bound:
                raise Problem(f"""All entries with the same placement must have the same lower bound as well (two placements found with bounds {curr_placement}-{curr_bound} 
                              and {placement.placement}-{placement.placement_lower_bound})""", status=400)
            # example: we should have exactly 3 placements with placement 3 and lower bound 5, so if the placement changes early throw a error
            if placement.placement != curr_placement and curr_bound is not None and i != curr_bound:
                raise Problem(f"""Expected {curr_bound - curr_placement + 1} placements with value {curr_placement}-{curr_bound}, but only found {i - curr_placement + 1}""",
                              status=400)
            
            if placement.placement_lower_bound != curr_bound and placement.placement_lower_bound is not None:
                if placement.placement_lower_bound <= i+1:
                    raise Problem(f"Error in placement for ID {placement.registration_id}: Placement lower bound should always be greater than placement", status=400)
                if placement.placement_lower_bound >= len(sorted_placements):
                    raise Problem(f"Error in placement for ID {placement.registration_id}: Placement lower bound should not be higher than total num of placements", status=400)

            if placement.placement != curr_placement:
                curr_placement = i+1
            if placement.placement_lower_bound != curr_bound:
                curr_bound = placement.placement_lower_bound
            
        async with db_wrapper.connect() as db:
            params = [(self.tournament_id, p.registration_id, p.placement, p.placement_description, p.placement_lower_bound, p.is_disqualified) for p in b]
            if self.is_squad:
                await db.execute("DELETE FROM tournament_squad_placements WHERE tournament_id = ?", (self.tournament_id,))
                await db.executemany("""INSERT INTO tournament_squad_placements(
                                        tournament_id, squad_id, placement, placement_description, placement_lower_bound, is_disqualified
                                        ) VALUES (?, ?, ?, ?, ?, ?)""", params)
            else:
                await db.execute("DELETE FROM tournament_solo_placements WHERE tournament_id = ?", (self.tournament_id,))
                await db.executemany("""INSERT INTO tournament_solo_placements(
                                        tournament_id, player_id, placement, placement_description, placement_lower_bound, is_disqualified
                                        ) VALUES (?, ?, ?, ?, ?, ?)""", params)
            await db.commit()

@dataclass
class GetSoloPlacementsCommand(Command[TournamentPlacementList]):
    tournament_id: int
    players: list[TournamentPlayerDetails]

    async def handle(self, db_wrapper, s3_wrapper):
        player_dict = {player.id: player for player in self.players}
        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute("""SELECT player_id, placement, placement_description, placement_lower_bound, is_disqualified FROM tournament_solo_placements WHERE tournament_id = ?""", (self.tournament_id,)) as cursor:
                rows = await cursor.fetchall()
                placed_players = [TournamentPlacementDetailed(reg_id, placement, placement_description, placement_lower_bound, is_dq, player_dict[reg_id], None) 
                                  for reg_id, placement, placement_description, placement_lower_bound, is_dq in rows]
                placed_ids = [p.registration_id for p in placed_players]
                unplaced_players = [TournamentPlacementDetailed(player.id, None, None, None, False, player, None) for player in self.players if player.id not in placed_ids]
                return TournamentPlacementList(self.tournament_id, False, placed_players, unplaced_players)
            
@dataclass
class GetSquadPlacementsCommand(Command[TournamentPlacementList]):
    tournament_id: int
    squads: list[TournamentSquadDetails]

    async def handle(self, db_wrapper, s3_wrapper):
        squad_dict = {squad.id: squad for squad in self.squads}
        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute("SELECT squad_id, placement, placement_description, placement_lower_bound, is_disqualified FROM tournament_squad_placements WHERE tournament_id = ?", (self.tournament_id,)) as cursor:
                rows = await cursor.fetchall()
                placed_squads = [TournamentPlacementDetailed(reg_id, placement, placement_description, placement_lower_bound, is_dq, None, squad_dict[reg_id]) 
                                 for reg_id, placement, placement_description, placement_lower_bound, is_dq in rows]
                placed_ids = [p.registration_id for p in placed_squads]
                unplaced_squads = [TournamentPlacementDetailed(squad.id, None, None, None, False, None, squad) for squad in self.squads if squad.id not in placed_ids]
                return TournamentPlacementList(self.tournament_id, True, placed_squads, unplaced_squads)

