from dataclasses import dataclass
from typing import List

from common.data.commands import Command
from common.data.models import *


@dataclass
class SetPlacementsCommand(Command[None]):
    tournament_id: int
    body: list[TournamentPlacement]

    async def handle(self, db_wrapper, s3_wrapper):
        b = self.body
        async with db_wrapper.connect() as db:
            # get tournament format
            async with db.execute("SELECT is_squad FROM tournaments WHERE id = ?", (self.tournament_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem("Tournament not found", status=404)
                is_squad = row[0]
                is_squad =  bool(is_squad)

            if not is_squad:
                params = [(self.tournament_id, p.registration_id, p.placement, p.placement_description) for p in b]
                await db.execute("DELETE FROM tournament_solo_placements WHERE tournament_id = ?", (self.tournament_id,))
                await db.executemany("""INSERT INTO tournament_solo_placements(
                                            tournament_id, player_id, placement, placement_description
                                            ) VALUES (?, ?, ?, ?)""", params)
            else:
                params = [(self.tournament_id, p.registration_id, p.placement, p.placement_description) for p in b]
                await db.execute("DELETE FROM tournament_squad_placements WHERE tournament_id = ?", (self.tournament_id,))
                await db.executemany("""INSERT INTO tournament_squad_placements(
                                            tournament_id, squad_id, placement, placement_description
                                            ) VALUES (?, ?, ?, ?)""", params)
            await db.commit()


@dataclass
class GetSoloPlacementsCommand(Command[TournamentPlacementList]):
    tournament_id: int
    players: list[TournamentPlayerDetails]

    async def handle(self, db_wrapper, s3_wrapper):
        player_dict = {player.id: player for player in self.players}
        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute("""SELECT player_id, placement, placement_description FROM tournament_solo_placements WHERE tournament_id = ?""", (self.tournament_id,)) as cursor:
                rows = await cursor.fetchall()
                placed_players = [TournamentPlacementDetailed(reg_id, placement, placement_description, player_dict[reg_id], None) for reg_id, placement, placement_description in rows]
                placed_ids = [p.registration_id for p in placed_players]
                unplaced_players = [TournamentPlacementDetailed(player.id, None, None, player, None) for player in self.players if player.id not in placed_ids]
                return TournamentPlacementList(self.tournament_id, False, placed_players, unplaced_players)
            
@dataclass
class GetSquadPlacementsCommand(Command[TournamentPlacementList]):
    tournament_id: int
    squads: list[TournamentSquadDetails]

    async def handle(self, db_wrapper, s3_wrapper):
        squad_dict = {squad.id: squad for squad in self.squads}
        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute("SELECT squad_id, placement, placement_description FROM tournament_squad_placements WHERE tournament_id = ?", (self.tournament_id,)) as cursor:
                rows = await cursor.fetchall()
                placed_squads = [TournamentPlacementDetailed(reg_id, placement, placement_description, None, squad_dict[reg_id]) for reg_id, placement, placement_description in rows]
                placed_ids = [p.registration_id for p in placed_squads]
                unplaced_squads = [TournamentPlacementDetailed(squad.id, None, None, None, squad) for squad in self.squads if squad.id not in placed_ids]
                return TournamentPlacementList(self.tournament_id, True, placed_squads, unplaced_squads)

