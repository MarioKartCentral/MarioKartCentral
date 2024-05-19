from dataclasses import dataclass
from typing import List
from common.data.models import TournamentPlayerDetails, TournamentSquadDetails

@dataclass
class TournamentPlacement():
    registration_id: int
    placement: int | None
    placement_description: str | None

@dataclass
class TournamentPlacementDetailed(TournamentPlacement):
    player: TournamentPlayerDetails | None
    squad: TournamentSquadDetails | None

@dataclass
class TournamentPlacementList():
    tournament_id: int
    is_squad: bool
    placements: list[TournamentPlacementDetailed]
    unplaced: list[TournamentPlacementDetailed]

# @dataclass
# class SetPlacements():
#     placements: List[TournamentPlacement]

# @dataclass
# class GetPlacementsData():
#     placements: List[TournamentPlacement]