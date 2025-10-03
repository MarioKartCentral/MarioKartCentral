from dataclasses import dataclass

from common.data.commands import Command, save_to_command_log
from common.data.models import *
from datetime import datetime, timezone

@save_to_command_log
@dataclass
class SetTournamentPlacementsCommand(Command[None]):
    tournament_id: int
    body: list[TournamentPlacement]
    registrations: list[TournamentSquadDetails]
    
    async def handle(self, db_wrapper, s3_wrapper):
        b = self.body
        registration_dict = {reg.id: reg for reg in self.registrations}
        # sort with DQs at the end
        sorted_placements = sorted(b, key=lambda x: float('inf') if x.placement is None else x.placement)

        # going through placements in order of rank to make sure they fulfill all criteria
        curr_placement = 1
        curr_bound = None
        for i, placement in enumerate(sorted_placements):
            if placement.placement_description and len(placement.placement_description) > 32:
                raise Problem("Placement descriptions must be 32 characters or less", status=400)
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
            await db.execute("DELETE FROM tournament_placements WHERE tournament_id = ?", (self.tournament_id,))
            await db.executemany("""INSERT INTO tournament_placements(
                                    tournament_id, registration_id, placement, placement_description, placement_lower_bound, is_disqualified
                                    ) VALUES (?, ?, ?, ?, ?, ?)""", params)
            await db.commit()

@save_to_command_log
@dataclass
class SetTournamentPlacementsFromPlayerIDsCommand(Command[None]):
    tournament_id: int
    body: list[TournamentPlacementFromPlayerIDs]

    async def handle(self, db_wrapper, s3_wrapper):
        b = self.body
        # sort with DQs at the end
        sorted_placements = sorted(b, key=lambda x: float('inf') if x.placement is None else x.placement)
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT min_squad_size, max_squad_size, is_squad FROM tournaments WHERE id = ?", (self.tournament_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Tournament not found", status=404)
                min_squad_size, max_squad_size, is_squad = row

        # going through placements in order of rank to make sure they fulfill all criteria
        curr_placement = 1
        curr_bound = None
        for i, placement in enumerate(sorted_placements):
            if placement.placement_description and len(placement.placement_description) > 32:
                raise Problem("Placement descriptions must be 32 characters or less", status=400)
            if placement.placement is None:
                if not placement.is_disqualified:
                    raise Problem("Cannot have null placement value when not disqualified", status=400)
                if placement.placement_lower_bound:
                    raise Problem("Placement must be non-null to set lower bound", status=400)
                if placement.placement_description:
                    raise Problem("Cannot have description for null placements", status=400)
            if is_squad:
                if min_squad_size is not None and len(placement.player_ids) < min_squad_size:
                    raise Problem(f"Error in placement for ID {placement.player_ids}: Row has less players than minimum squad size", status=400)
                if max_squad_size is not None and len(placement.player_ids) > max_squad_size:
                    raise Problem(f"Error in placement for ID {placement.player_ids}: Row has more players than maximum squad size", status=400)
            else:
                if len(placement.player_ids) > 1:
                    raise Problem(f"Error in placement for ID {placement.player_ids}: Row has more than 1 player for a solo tournament", status=400)
            if placement.placement and placement.is_disqualified:
                raise Problem("Cannot have a placement value while disqualified", status=400)
            # if the current placement is not equal to its sorted position in the list or is not tied with the previous placement
            if placement.placement is not None and placement.placement != i+1 and placement.placement != curr_placement:
                raise Problem(f"Error processing placements: Placement for ID {placement.player_ids} has value {placement.placement} instead of {i+1} or {curr_placement}", status=400)
            if i > 0 and placement.placement == curr_placement and placement.placement_lower_bound != curr_bound:
                raise Problem(f"""All entries with the same placement must have the same lower bound as well (two placements found with bounds {curr_placement}-{curr_bound} 
                              and {placement.placement}-{placement.placement_lower_bound})""", status=400)
            # example: we should have exactly 3 placements with placement 3 and lower bound 5, so if the placement changes early throw a error
            if placement.placement != curr_placement and curr_bound is not None and i != curr_bound:
                raise Problem(f"""Expected {curr_bound - curr_placement + 1} placements with value {curr_placement}-{curr_bound}, but only found {i - curr_placement + 1}""",
                              status=400)
            
            if placement.placement_lower_bound != curr_bound and placement.placement_lower_bound is not None:
                if placement.placement_lower_bound <= i+1:
                    raise Problem(f"Error in placement for ID {placement.player_ids}: Placement lower bound should always be greater than placement", status=400)
                if placement.placement_lower_bound >= len(sorted_placements):
                    raise Problem(f"Error in placement for ID {placement.player_ids}: Placement lower bound should not be higher than total num of placements", status=400)

            if placement.placement != curr_placement:
                curr_placement = i+1
            if placement.placement_lower_bound != curr_bound:
                curr_bound = placement.placement_lower_bound
            
        squad_dict: dict[int, TournamentPlacementFromPlayerIDs] = {}
        now = int(datetime.now(timezone.utc).timestamp())
        async with db_wrapper.connect() as db:
            await db.execute("DELETE FROM tournament_placements WHERE tournament_id = ?", (self.tournament_id,))
            await db.execute("DELETE FROM tournament_players WHERE tournament_id = ?", (self.tournament_id,))
            await db.execute("DELETE FROM tournament_registrations WHERE tournament_id = ?", (self.tournament_id,))
            for placement in sorted_placements:
                async with db.execute("""INSERT INTO tournament_registrations(color, timestamp, tournament_id, is_registered, is_approved)
                                    VALUES(?, ?, ?, ?, ?)""", (0, now, self.tournament_id, True, True)) as cursor:
                    registration_id = cursor.lastrowid
                    if registration_id:
                        squad_dict[registration_id] = placement

            player_rows = [(player_id, self.tournament_id, registration_id, False, now, False, None, False, False, None, False, False, True, player_id) 
                           for registration_id, placement in squad_dict.items() for player_id in placement.player_ids]
            await db.executemany("""INSERT INTO tournament_players(player_id, tournament_id, registration_id, is_squad_captain, timestamp, is_checked_in,
                                    mii_name, can_host, is_invite, selected_fc_id, is_representative, is_bagger_clause, is_approved)
                                    SELECT ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                                    WHERE EXISTS (SELECT 1 FROM players WHERE id = ?)""", player_rows)
            placement_rows = [(self.tournament_id, registration_id, placement.placement, placement.placement_description,
                               placement.placement_lower_bound, placement.is_disqualified) for registration_id, placement in squad_dict.items()]
            await db.executemany("""INSERT INTO tournament_placements(tournament_id, registration_id, placement, placement_description, 
                                 placement_lower_bound, is_disqualified) VALUES(?, ?, ?, ?, ?, ?)""", placement_rows)
            await db.commit()

@dataclass
class GetTournamentPlacementsCommand(Command[TournamentPlacementList]):
    tournament_id: int
    squads: list[TournamentSquadDetails]

    async def handle(self, db_wrapper, s3_wrapper):
        squad_dict = {squad.id: squad for squad in self.squads}
        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute("SELECT registration_id, placement, placement_description, placement_lower_bound, is_disqualified FROM tournament_placements WHERE tournament_id = ? ORDER BY placement", (self.tournament_id,)) as cursor:
                rows = await cursor.fetchall()
                placed_squads: list[TournamentPlacementDetailed] = []
                for row in rows:
                    reg_id, placement, placement_description, placement_lower_bound, is_dq = row
                    squad = squad_dict.get(reg_id, None)
                    if not squad:
                        continue
                    placed_squads.append(TournamentPlacementDetailed(reg_id, placement, placement_description, placement_lower_bound, is_dq, squad))
                placed_ids = [p.registration_id for p in placed_squads]
                unplaced_squads = [TournamentPlacementDetailed(squad.id, None, None, None, False, squad) for squad in self.squads if squad.id not in placed_ids]
                return TournamentPlacementList(self.tournament_id, placed_squads, unplaced_squads)

@dataclass
class GetPlayerTournamentPlacementsCommand(Command[PlayerTournamentResults]):
    """
    Get all tournament placement data for a particular player
    - Solo, Squad, & Team
    """
    player_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        tournament_solo_and_squad_results: list[PlayerTournamentPlacement] = []
        tournament_team_results: list[PlayerTournamentPlacement] = []
        async with db_wrapper.connect(readonly=True) as db:
            # Solo + Squad placements (squad tournaments with squad size 1-4)
            squad_dict: dict[int, PlayerTournamentPlacement] = {}
            async with db.execute("""
                SELECT t.id as "tournament_id", t.name as "tournament_name", t.game, t.mode, s.id, s.name, t.date_start, t.date_end, tsp.placement, tsp.placement_description, tsp.is_disqualified
                FROM tournament_players as tp 
                INNER JOIN tournaments as t
                ON tp.tournament_id = t.id
                JOIN tournament_registrations s ON s.id = tp.registration_id
                LEFT JOIN tournament_placements as tsp 
                ON s.id = tsp.registration_id
                WHERE t.show_on_profiles = 1
                AND t.is_public = 1
                AND tp.registration_id IS NOT NULL
                AND t.teams_allowed = 0
                AND (t.min_squad_size IS NULL OR t.min_squad_size <= 4)
                AND tp.player_id = ?
                AND tp.is_invite = 0
                AND s.is_registered = 1
                """, (self.player_id,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    tournament_id, tournament_name, game, mode, registration_id, squad_name, date_start, date_end, placement, placement_description, is_disqualified = row
                    squad_placement = PlayerTournamentPlacement(tournament_id, tournament_name, game, mode, registration_id, squad_name, None, date_start, date_end, placement, placement_description, is_disqualified, [], [])
                    squad_dict[registration_id] = squad_placement
                    tournament_solo_and_squad_results.append(squad_placement)

            # Get partner information
            async with db.execute("""
                SELECT tp.player_id, p.name, tp.registration_id
                FROM tournament_players as tp
                INNER JOIN tournament_placements as tsp
                ON tp.registration_id = tsp.registration_id
                INNER JOIN tournament_registrations as ts
                ON tsp.registration_id = ts.id
                INNER JOIN players as p
                ON p.id = tp.player_id
                WHERE tsp.registration_id 
                IN (SELECT registration_id FROM tournament_players WHERE player_id = ?)
                AND tsp.registration_id NOT IN (SELECT registration_id FROM team_squad_registrations)
                AND tp.player_id <> ?;
                """, (self.player_id,self.player_id)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    player_id, player_name, registration_id = row
                    if registration_id in squad_dict:
                        partner_details = TournamentPlayerDetailsShort(player_id, player_name, registration_id)
                        squad_dict[registration_id].partners.append(partner_details)

            team_placement_dict: dict[int, PlayerTournamentPlacement] = {}
            # Team placements (either tournaments which allow teams or tournaments with squad size >4)
            async with db.execute("""
                SELECT DISTINCT t.id, t.name, t.game, t.mode, s.id, s.name, t.date_start, t.date_end, tsp.placement, tsp.placement_description, tsp.is_disqualified
                FROM tournament_players as tp 
                INNER JOIN tournaments as t
                ON tp.tournament_id = t.id 
                JOIN tournament_registrations s ON s.id = tp.registration_id
                LEFT JOIN tournament_placements as tsp 
                ON tp.registration_id = tsp.registration_id
                LEFT JOIN team_squad_registrations as tsr
                ON s.id = tsr.registration_id
                LEFT JOIN team_rosters as tr ON
                tsr.roster_id = tr.id
                LEFT JOIN teams
                ON tr.team_id = teams.id
                WHERE t.show_on_profiles = 1
                AND t.is_public = 1
                AND tp.registration_id IS NOT NULL
                AND tp.player_id = ?
                AND s.is_registered = 1
                AND (t.teams_allowed = 1 OR t.min_squad_size > 4)
                ORDER BY t.date_start DESC;
                """, (self.player_id,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    (tournament_id, tournament_name, game, mode, registration_id, squad_name,
                      date_start, date_end, placement, placement_description, is_disqualified) = row
                    placement_obj = PlayerTournamentPlacement(tournament_id, tournament_name, game, mode, registration_id, 
                                                                             squad_name, None, date_start, date_end, placement, placement_description, is_disqualified, [], [])
                    tournament_team_results.append(placement_obj)
                    team_placement_dict[registration_id] = placement_obj
                    
            # get teams from team placements
            async with db.execute("""
                SELECT DISTINCT s.id, tr.id, tr.name, tr.tag, teams.id, teams.name, teams.tag, teams.color
                FROM tournament_players as tp 
                INNER JOIN tournaments as t
                ON tp.tournament_id = t.id 
                JOIN tournament_registrations s ON s.id = tp.registration_id
                JOIN team_squad_registrations as tsr
                ON s.id = tsr.registration_id
                JOIN team_rosters as tr ON
                tsr.roster_id = tr.id
                JOIN teams
                ON tr.team_id = teams.id
                WHERE t.show_on_profiles = 1
                AND t.is_public = 1
                AND tp.registration_id IS NOT NULL
                AND tp.player_id = ?
                AND s.is_registered = 1
                AND (t.teams_allowed = 1 OR t.min_squad_size > 4)
                ORDER BY t.date_start DESC;
                """, (self.player_id,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    registration_id, roster_id, roster_name, roster_tag, team_id, team_name, team_tag, team_color = row
                    placement_obj = team_placement_dict.get(registration_id, None)
                    if placement_obj:
                        if roster_name is None:
                            roster_name = team_name
                        if roster_tag is None:
                            roster_tag = team_tag
                        if placement_obj.squad_name is None:
                            placement_obj.squad_name = roster_name
                        if placement_obj.team_id is None:
                            placement_obj.team_id = team_id
                        placement_obj.rosters.append(RosterBasic(team_id, team_name, team_tag, team_color, roster_id, roster_name, roster_tag))

            results = PlayerTournamentResults(tournament_solo_and_squad_results, tournament_team_results)
            return results

@dataclass
class GetTeamTournamentPlacementsCommand(Command[TeamTournamentResults]):
    """
    Get all tournament placement data for a particular team
    """
    team_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        tournament_team_results: list[TeamTournamentPlacement] = []
        async with db_wrapper.connect(readonly=True) as db:
            team_placement_dict: dict[int, TeamTournamentPlacement] = {}
            # Team placements
            async with db.execute("""
                SELECT DISTINCT s.id, s.name, t.id as "tournament_id", t.name as "tournament_name", t.game, t.mode, t.date_start, t.date_end, tsp.placement, tsp.placement_description, tsp.is_disqualified
                FROM tournaments as t
                JOIN tournament_registrations s ON s.tournament_id = t.id
                INNER JOIN team_squad_registrations as tsr
                ON tsr.registration_id = s.id
                LEFT JOIN tournament_placements as tsp 
                ON tsr.registration_id = tsp.registration_id
                INNER JOIN team_rosters as tr ON
                tsr.roster_id = tr.id
                INNER JOIN teams
                ON tr.team_id = teams.id
                WHERE t.show_on_profiles = 1
                AND teams.id = ?
                AND s.is_registered = 1
                ORDER BY t.date_start DESC;
                """, (self.team_id,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    registration_id, squad_name, tournament_id, tournament_name, game, mode, date_start, date_end, placement, placement_description, is_disqualified = row
                    placement_obj = TeamTournamentPlacement(tournament_id, tournament_name, game, mode, registration_id, squad_name, date_start, date_end, placement, placement_description,
                                                                           is_disqualified, [])
                    tournament_team_results.append(placement_obj)
                    team_placement_dict[registration_id] = placement_obj

            async with db.execute("""
                SELECT DISTINCT s.id, teams.id, teams.name, teams.tag, teams.color, tr.id, tr.name, tr.tag
                FROM tournaments as t
                JOIN tournament_registrations s ON s.tournament_id = t.id
                INNER JOIN team_squad_registrations as tsr
                ON tsr.registration_id = s.id
                LEFT JOIN tournament_placements as tsp 
                ON tsr.registration_id = tsp.registration_id
                INNER JOIN team_rosters as tr ON
                tsr.roster_id = tr.id
                INNER JOIN teams
                ON tr.team_id = teams.id
                WHERE t.show_on_profiles = 1
                AND teams.id = ?
                AND s.is_registered = 1
                ORDER BY t.date_start DESC;
                """, (self.team_id,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    registration_id, team_id, team_name, team_tag, team_color, roster_id, roster_name, roster_tag = row
                    placement_obj = team_placement_dict[registration_id]
                    if placement_obj:
                        if roster_name is None:
                            roster_name = team_name
                        if roster_tag is None:
                            roster_tag = team_tag
                        if placement_obj.squad_name is None:
                            placement_obj.squad_name = roster_name
                        roster = RosterBasic(team_id, team_name, team_tag, team_color, roster_id, roster_name, roster_tag)
                        placement_obj.rosters.append(roster)
            results = TeamTournamentResults(tournament_team_results)
            return results

@dataclass
class GetLatestTournamentIdWithPlacements(Command[int]):
    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute("""
                SELECT id FROM tournaments where is_viewable = 1 AND is_public = 1 AND id IN (
                    SELECT tournament_id from tournament_placements
                ) ORDER BY date_end DESC LIMIT 1
                """) as cursor:
                row = await cursor.fetchone()
                if row is None or row[0] is None:
                    raise Problem('There are no tournaments with placements', status=404)
                return row[0]