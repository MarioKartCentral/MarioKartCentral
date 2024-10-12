from dataclasses import dataclass

from common.data.models.tournaments import CreateTournamentRequestData
from common.data.models.common import Game, GameMode


# @dataclass
# class TournamentTemplateRequestData(CreateTournamentRequestData):
#     template_name: str

@dataclass
class TournamentTemplateRequestData():
    template_name: str
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
class TournamentTemplate(TournamentTemplateRequestData):
    id: int | None

@dataclass
class TournamentTemplateMinimal():
    id: int
    template_name: str
    series_id: int | None

@dataclass
class TemplateFilter():
    series_id: int | None = None
