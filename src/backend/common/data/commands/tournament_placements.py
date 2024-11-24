from dataclasses import dataclass

from common.data.commands import Command, save_to_command_log
from common.data.db.tables import TournamentPlayer
from common.data.models import *
from json import dumps as jason_dumps

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


@dataclass
class GetPlayerTournamentPlacementsCommand(Command[PlayerTournamentResults]):
    """
    Get all tournament placement data for a particular player
    - Solo, Squad, & Team
    """
    player_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        tournament_solo_and_squad_results = []
        tournament_team_results = []
        async with db_wrapper.connect(readonly=True) as db:
            # Solo placements
            async with db.execute("""
                SELECT t.id as "tournament_id", t.name as "tournament_name", t.game, t.mode, t.date_start, t.date_end, tsp.placement, tsp.placement_description, tsp.is_disqualified
                FROM tournament_players as tp 
                INNER JOIN tournaments as t
                ON tp.tournament_id = t.id 
                LEFT JOIN tournament_solo_placements as tsp 
                ON tp.id = tsp.player_id
                WHERE t.show_on_profiles = 1
                AND tp.squad_id IS NULL
                AND t.teams_only = 0
                AND tp.player_id = ?
                """, (self.player_id,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    tournament_id, tournament_name, game, mode, date_start, date_end, placement, placement_description, is_disqualified = row
                    tournament_solo_and_squad_results.append(PlayerTournamentPlacement(tournament_id, tournament_name, game, mode, None, None, None, date_start, date_end, placement, placement_description, is_disqualified, []))

            # Squad placements
            squad_dict: dict[int, PlayerTournamentPlacement] = {}
            async with db.execute("""
                SELECT t.id as "tournament_id", t.name as "tournament_name", t.game, t.mode, tsp.squad_id, t.date_start, t.date_end, tsp.placement, tsp.placement_description, tsp.is_disqualified
                FROM tournament_players as tp 
                INNER JOIN tournaments as t
                ON tp.tournament_id = t.id 
                LEFT JOIN tournament_squad_placements as tsp 
                ON tp.squad_id = tsp.squad_id
                WHERE t.show_on_profiles = 1
                AND tp.squad_id IS NOT NULL
                AND t.teams_only = 0
                AND tp.player_id = ?
                """, (self.player_id,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    tournament_id, tournament_name, game, mode, squad_id, date_start, date_end, placement, placement_description, is_disqualified = row
                    squad_placement = PlayerTournamentPlacement(tournament_id, tournament_name, game, mode, squad_id, None, None, date_start, date_end, placement, placement_description, is_disqualified, [])
                    squad_dict[squad_id] = squad_placement
                    tournament_solo_and_squad_results.append(squad_placement)

            # Get partner information
            async with db.execute("""
                SELECT tp.player_id, p.name, tp.squad_id
                FROM tournament_players as tp
                INNER JOIN tournament_squad_placements as tsp
                ON tp.squad_id = tsp.squad_id
                INNER JOIN tournament_squads as ts
                ON tsp.squad_id = ts.id
                INNER JOIN players as p
                ON p.id = tp.player_id
                WHERE tsp.squad_id 
                IN (SELECT squad_id FROM tournament_players WHERE player_id = ?)
                AND tsp.squad_id NOT IN (SELECT squad_id FROM team_squad_registrations)
                AND tp.player_id <> ?;
                """, (self.player_id,self.player_id)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    player_id, player_name, squad_id = row
                    if squad_id in squad_dict:
                        partner_details = TournamentPlayerDetailsShort(player_id, player_name, squad_id)
                        squad_dict[squad_id].partners.append(partner_details)

            # Team placements
            async with db.execute("""
                SELECT t.id as "tournament_id", t.name as "tournament_name", t.game, t.mode, tsp.squad_id, teams.name as "squad_name", teams.id as "team_id", t.date_start, t.date_end, tsp.placement, tsp.placement_description, tsp.is_disqualified
                FROM tournament_players as tp 
                INNER JOIN tournaments as t
                ON tp.tournament_id = t.id 
                LEFT JOIN tournament_squad_placements as tsp 
                ON tp.squad_id = tsp.squad_id
                INNER JOIN team_squad_registrations as tsr
                ON tp.squad_id = tsr.squad_id
                INNER JOIN team_rosters as tr ON
                tsr.roster_id = tr.id
                INNER JOIN teams
                ON tr.team_id = teams.id
                WHERE t.show_on_profiles = 1
                AND tp.squad_id IS NOT NULL
                AND tsp.squad_id IN (SELECT squad_id FROM team_squad_registrations)
                AND tp.player_id = ?
                ORDER BY t.date_start DESC;
                """, (self.player_id,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    tournament_id, tournament_name, game, mode, squad_id, squad_name, team_id, date_start, date_end, placement, placement_description, is_disqualified = row
                    tournament_team_results.append(PlayerTournamentPlacement(tournament_id, tournament_name, game, mode, squad_id, squad_name, team_id, date_start, date_end, placement, placement_description, is_disqualified, []))
                results = PlayerTournamentResults(tournament_solo_and_squad_results, tournament_team_results)
                return results


@dataclass
class GetTeamTournamentPlacementsCommand(Command[TeamTournamentResults]):
    """
    Get all tournament placement data for a particular team
    - Solo, Squad, & Team
    """
    team_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        tournament_team_results = []
        async with db_wrapper.connect(readonly=True) as db:
            # Team placements
            async with db.execute("""
                SELECT t.id as "tournament_id", t.name as "tournament_name", t.game, t.mode, teams.id as "team_id", t.date_start, t.date_end, tsp.placement, tsp.placement_description, tsp.is_disqualified
                FROM tournaments as t
                LEFT JOIN tournament_squad_placements as tsp 
                ON t.id = tsp.tournament_id
                INNER JOIN team_squad_registrations as tsr
                ON tsp.squad_id = tsr.squad_id
                INNER JOIN team_rosters as tr ON
                tsr.roster_id = tr.id
                INNER JOIN teams
                ON tr.team_id = teams.id
                WHERE t.show_on_profiles = 1
                AND teams.id = ?
                ORDER BY t.date_start DESC;
                """, (self.team_id,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    tournament_id, tournament_name, game, mode, team_id, date_start, date_end, placement, placement_description, is_disqualified = row
                    tournament_team_results.append(TeamTournamentPlacement(tournament_id, tournament_name, game, mode, team_id, date_start, date_end, placement, placement_description, is_disqualified))
                results = TeamTournamentResults(tournament_team_results)
                return results
