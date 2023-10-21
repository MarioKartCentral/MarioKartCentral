from dataclasses import dataclass

from common.data.validators import validate_game_and_mode


@dataclass
class CreateTournamentRequestData():
    tournament_name: str
    game: str
    mode: str
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

    def __post_init__(self):
        validate_game_and_mode(self.game, self.mode)

@dataclass
class GetTournamentRequestData(CreateTournamentRequestData):
    id: int
    series_name: str | None = None
    series_url: str | None = None
    series_description: str | None = None

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
    verified_fc_required: bool
    is_viewable: bool
    is_public: bool
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
    game: str
    mode: str
    date_start: int
    date_end: int

    def __post_init__(self):
        validate_game_and_mode(self.game, self.mode)

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
    game: str | None = None
    mode: str | None = None
    series_id: int | None = None
    is_viewable: bool | None = None
    is_public: bool | None = None

    def __post_init__(self):
        if self.game is not None and self.mode is not None:
            validate_game_and_mode(self.game, self.mode)