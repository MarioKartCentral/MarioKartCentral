from dataclasses import dataclass

from common.data.models.common import Game, GameMode
from common.data.models.tournament_placements import TournamentPlacementDetailed

@dataclass
class TournamentDBFields():
    name: str
    game: Game
    mode: GameMode
    series_id: int | None
    is_squad: bool
    registrations_open: bool
    date_start: int
    date_end: int
    use_series_description: bool
    series_stats_include: bool
    use_series_logo: bool
    url: str | None
    registration_deadline: int | None
    registration_cap: int | None
    teams_allowed: bool
    teams_only: bool
    team_members_only: bool
    min_squad_size: int | None
    max_squad_size: int | None
    squad_tag_required: bool
    squad_name_required: bool
    mii_name_required: bool
    host_status_required: bool
    checkins_enabled: bool
    checkins_open: bool
    min_players_checkin: int | None
    verification_required: bool
    verified_fc_required: bool
    is_viewable: bool
    is_public: bool
    is_deleted: bool
    show_on_profiles: bool
    require_single_fc: bool
    min_representatives: int | None
    bagger_clause_enabled: bool
    use_series_ruleset: bool
    organizer: str
    location: str | None

@dataclass
class TournamentS3Fields():
    description: str
    ruleset: str

@dataclass
class CreateTournamentRequestData(TournamentDBFields, TournamentS3Fields): 
    logo_file: str | None

@dataclass
class GetTournamentRequestData(TournamentDBFields, TournamentS3Fields):
    id: int
    is_deleted: bool
    logo: str | None
    series_name: str | None = None
    series_url: str | None = None
    series_description: str | None = None
    series_ruleset: str | None = None
    
@dataclass
class EditTournamentRequestData():
    name: str
    series_id: int | None
    registrations_open: bool
    date_start: int
    date_end: int
    use_series_description: bool
    series_stats_include: bool
    use_series_logo: bool
    url: str | None
    registration_deadline: int | None
    registration_cap: int | None
    min_squad_size: int | None
    max_squad_size: int | None
    checkins_enabled: bool
    checkins_open: bool
    min_players_checkin: int | None
    verification_required: bool
    verified_fc_required: bool
    is_viewable: bool
    is_public: bool
    is_deleted: bool
    show_on_profiles: bool
    min_representatives: int | None
    bagger_clause_enabled: bool
    use_series_ruleset: bool
    organizer: str | None
    location: str | None
    # s3-only fields below
    description: str
    ruleset: str
    # logo fields
    logo_file: str | None
    remove_logo: bool

@dataclass
class TournamentDataMinimal():
    id: int
    name: str
    game: Game
    mode: GameMode
    date_start: int
    date_end: int

@dataclass
class TournamentDataBasic(TournamentDataMinimal):
    series_id: int | None
    series_name: str | None
    series_url: str | None
    series_short_description: str | None
    is_squad: bool
    registrations_open: bool
    teams_allowed: bool
    logo: str | None
    use_series_logo: bool
    is_viewable: bool
    is_public: bool
    organizer: str

@dataclass
class TournamentList:
    tournaments: list[TournamentDataBasic]
    tournament_count: int
    page_count: int

@dataclass
class TournamentFilter:
    name: str | None = None
    game: Game | None = None
    mode: GameMode | None = None
    series_id: int | None = None
    is_viewable: bool | None = None
    is_public: bool | None = None
    from_date: int | None = None
    to_date: int | None = None
    page: int | None = None

@dataclass
class TournamentInvite:
    invite_id: int
    tournament_id: int
    timestamp: int
    is_bagger_clause: bool
    squad_name: str | None
    squad_tag: str | None
    squad_color: int
    tournament_name: str
    tournament_game: Game
    tournament_mode: GameMode

@dataclass
class TournamentWithPlacements(TournamentDataBasic):
    placements: list[TournamentPlacementDetailed]