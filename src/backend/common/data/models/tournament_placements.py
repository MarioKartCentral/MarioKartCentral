from dataclasses import dataclass
from common.data.models.squads import TournamentSquadDetails
from common.data.models.tournament_registrations import TournamentPlayerDetailsShort
from common.data.models.teams import RosterBasic

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
    squad: TournamentSquadDetails

@dataclass
class TournamentPlacementList():
    tournament_id: int
    placements: list[TournamentPlacementDetailed]
    unplaced: list[TournamentPlacementDetailed]

@dataclass
class PlayerTournamentPlacement():
    tournament_id: int
    tournament_name: str
    game: str
    mode: str
    registration_id: int
    squad_name: str | None
    team_id: int | None
    date_start: int
    date_end: int
    placement: int | None
    placement_description: str | None
    is_disqualified: bool
    partners: list[TournamentPlayerDetailsShort]
    rosters: list[RosterBasic]

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
    registration_id: int
    squad_name: str | None
    date_start: int
    date_end: int
    placement: int | None
    placement_description: str | None
    is_disqualified: bool
    rosters: list[RosterBasic]

@dataclass
class TeamTournamentResults():
    tournament_team_placements: list[TeamTournamentPlacement]
