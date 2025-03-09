from dataclasses import dataclass
from common.data.models import TournamentPlayerDetails, TournamentSquadDetails
from common.data.models.tournament_registrations import TournamentPlayerDetailsShort

@dataclass
class TournamentPlacement():
    registration_id: int
    placement: int | None
    placement_description: str | None
    placement_lower_bound: int | None
    is_disqualified: bool

@dataclass
class TournamentPlacementFromPlayerIDs():
    player_ids: list[int]
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

@dataclass
class PlayerTournamentPlacement():
    tournament_id: int
    tournament_name: str
    game: str
    mode: str
    squad_id: int | None
    squad_name: str | None
    team_id: int | None
    date_start: int
    date_end: int
    placement: int | None
    placement_description: str | None
    is_disqualified: bool
    partners: list[TournamentPlayerDetailsShort]

@dataclass
class PlayerTournamentResults():
    tournament_solo_and_squad_placements: list[PlayerTournamentPlacement]
    tournament_team_placements: list[PlayerTournamentPlacement]


@dataclass
class TeamTournamentPlacement():
    tournament_id: int
    tournament_name: str
    game: str
    mode: str
    team_id: int | None
    team_name: str | None
    date_start: int
    date_end: int
    placement: int | None
    placement_description: str | None
    is_disqualified: bool

@dataclass
class TeamTournamentResults():
    tournament_team_placements: list[TeamTournamentPlacement]