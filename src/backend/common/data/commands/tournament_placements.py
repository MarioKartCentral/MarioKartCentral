from dataclasses import dataclass
from typing import List

from common.data.commands import Command
from common.data.models import Problem, Placements, SetPlacements, GetPlacementsData


@dataclass
class SetPlacementsCommand(Command[None]):
    tournament_id: int
    body: SetPlacements

    async def handle(self, db_wrapper, s3_wrapper):
        b = self.body.placements
        async with db_wrapper.connect() as db:
            # get tournament format
            async with db.execute("SELECT is_squad FROM tournaments WHERE id = ?", (self.tournament_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem("Tournament not found", status=404)
                is_squad = row[0]
                is_squad =  bool(is_squad)

            if is_squad == False:
                for squad in b:
                    cursor = await db.execute("""INSERT INTO tournament_solo_placements(
                                            tournament_id, player_id, placement, placement_description
                                            ) VALUES (?, ?, ?, ?)""", (self.tournament_id, squad.squad_id, squad.placement, squad.placement_description))
            else:
                for squad in b:
                    cursor = await db.execute("""INSERT INTO tournament_squad_placements(
                                            tournament_id, squad_id, placement, placement_description
                                            ) VALUES (?, ?, ?, ?)""", (self.tournament_id, squad.squad_id, squad.placement, squad.placement_description))
            await db.commit()


@dataclass
class GetPlacementsCommand(Command[List[Placements]]):
    tournament_id: str
    is_squad: bool

    async def handle(self, db_wrapper, s3_wrapper) -> List[Placements]:
        async with db_wrapper.connect(readonly=True) as db:
            if self.is_squad == False:
                async with db.execute("""SELECT * FROM tournament_solo_placements WHERE tournament_id = ?""", (self.tournament_id,)) as cursor:
                    squad_rows = await cursor.fetchall()
            else:
                async with db.execute("""SELECT * FROM tournament_squad_placements WHERE tournament_id = ?""", (self.tournament_id,)) as cursor:
                    squad_rows = await cursor.fetchall()

            placements = [Placements(squad_id, placement, placement_description) for squad_id, placement, placement_description in squad_rows]

                    
            # placements = []
            # for squad in squad_rows:
            #     squad_id, placement, placement_description = squad
            #     data: Placements = Placements(squad_id, placement, placement_description)
            #     placements.append(data)

        return placements
