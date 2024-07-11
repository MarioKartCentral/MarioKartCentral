from dataclasses import dataclass
from common.data.models import TournamentPlayerDetails, TournamentSquadDetails

@dataclass
class TournamentPlacement():
    registration_id: int
    placement: int | None
    placement_description: str | None
    placement_lower_bound: int | None
    is_disqualified: bool

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

@dataclass
class TournamentSoloPlacements:
    id: int
    tournament_id: int
    player_id: int
    player_name: int
    placement: int
    placement_description: str
    placement_lower_bound: int | None
    is_disqualified: bool