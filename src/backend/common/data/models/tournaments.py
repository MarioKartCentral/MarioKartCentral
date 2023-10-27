from dataclasses import dataclass

from common.data.models.common import Game, GameMode


@dataclass
class CreateTournamentRequestData():
    tournament_name: str
    game: Game
    mode: GameMode
    series_id: int | None
    is_squad: bool
    registrations_open: bool
    date_start: int
    date_end: int
    description: str
    use_series_description: bool
    series_stats_include: bool
    logo: str | None
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
    checkins_open: bool
    min_players_checkin: int
    verification_required: bool
    verified_fc_required: bool
    is_viewable: bool
    is_public: bool
    show_on_profiles: bool
    require_single_fc: bool
    min_representatives: int | None
    # s3-only fields below
    ruleset: str
    use_series_ruleset: bool
    organizer: str
    location: str

@dataclass
class GetTournamentRequestData(CreateTournamentRequestData):
    id: int
    is_deleted: bool
    series_name: str | None = None
    series_url: str | None = None
    series_description: str | None = None
    series_ruleset: str | None = None
    

@dataclass
class EditTournamentRequestData():
    tournament_name: str
    series_id: int | None
    registrations_open: bool
    date_start: int
    date_end: int
    description: str
    use_series_description: bool
    series_stats_include: bool
    logo: str | None
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
    checkins_open: bool
    min_players_checkin: int
    verification_required: bool
    verified_fc_required: bool
    is_viewable: bool
    is_public: bool
    is_deleted: bool
    show_on_profiles: bool
    min_representatives: int | None
    # s3-only fields below
    ruleset: str
    use_series_ruleset: bool
    organizer: str
    location: str

@dataclass
class TournamentDataMinimal():
    id: int
    tournament_name: str
    game: Game
    mode: GameMode
    date_start: int
    date_end: int

@dataclass
class TournamentDataBasic(TournamentDataMinimal):
    series_id: int | None
    series_name: str | None
    series_url: str | None
    series_description: str | None
    is_squad: bool
    registrations_open: bool
    teams_allowed: bool
    description: str
    logo: str | None

@dataclass
class TournamentFilter():
    is_minimal: bool = False
    name: str | None = None
    game: Game | None = None
    mode: GameMode | None = None
    series_id: int | None = None
    is_viewable: bool | None = None
    is_public: bool | None = None

@dataclass
class TournamentInvite():
    invite_id: int
    tournament_id: int
    timestamp: int
    squad_name: str | None
    squad_tag: str | None
    squad_color: int
    tournament_name: str
    tournament_game: Game
    tournament_mode: GameMode