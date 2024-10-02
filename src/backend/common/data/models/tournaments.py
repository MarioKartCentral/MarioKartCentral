from dataclasses import dataclass

from common.data.models.common import Game, GameMode

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
    description: str
    use_series_description: bool
    series_stats_include: bool
    logo: str | None
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
    organizer: str | None
    location: str | None

@dataclass
class TournamentS3Fields():
    ruleset: str

@dataclass
# commented below randomly decides to not work for some reason
# class CreateTournamentRequestData(TournamentDBFields, TournamentS3Fields): pass
class CreateTournamentRequestData():
    name: str
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
    organizer: str | None
    location: str | None
    ruleset: str

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
    name: str
    series_id: int | None
    registrations_open: bool
    date_start: int
    date_end: int
    description: str
    use_series_description: bool
    series_stats_include: bool
    logo: str | None
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
    min_representatives: int | None
    bagger_clause_enabled: bool
    use_series_ruleset: bool
    organizer: str | None
    location: str | None
    # s3-only fields below
    ruleset: str

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
    series_description: str | None
    is_squad: bool
    registrations_open: bool
    teams_allowed: bool
    description: str
    logo: str | None
    use_series_logo: bool

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
    is_bagger_clause: bool
    squad_name: str | None
    squad_tag: str | None
    squad_color: int
    tournament_name: str
    tournament_game: Game
    tournament_mode: GameMode