from dataclasses import dataclass
from typing import Any, Dict, List, Literal

@dataclass
class Problem(Exception):
    """
    A schema for describing an error, based on RFC-7807: https://www.rfc-editor.org/rfc/rfc7807

    title: 
        A short, human-readable explanation of the error.
        The title should have the same value for all instances of this error.

    detail:
        An optional, more detailed human-readable explanation of the error.
        Additional information specific to this instance of the error can be included.

    data:
        An optional bag of additional data to go with the error
    """
    title: str
    detail: str | None = None
    status: int = 500
    data: Dict[str, Any] | None = None

Game = Literal["mkw", "mk7", "mk8", "mk8dx", "mkt"]
GameMode = Literal["150cc", "200cc", "rt", "ct"]
Approval = Literal["approved", "pending", "denied"]

@dataclass
class FriendCode:
    fc: str
    game: Game
    player_id: int
    is_verified: int
    is_primary: int

@dataclass
class User:
    id: int
    player_id: int | None

@dataclass
class UserLoginData(User):
    email: str
    password_hash: str

@dataclass
class Player:
    id: int
    name: str
    country_code: str
    is_hidden: bool
    is_shadow: bool
    is_banned: bool
    discord_id: str | None

@dataclass
class Squad:
    id: int
    name: str
    tag: str
    color: str
    is_registered: bool
    
@dataclass
class PlayerDetailed(Player):
    friend_codes: List[FriendCode]
    user: User | None

@dataclass
class CreatePlayerRequestData:
    name: str
    country_code: str
    is_hidden: bool = False
    is_shadow: bool = False
    is_banned: bool = False
    discord_id: str | None = None

@dataclass
class EditPlayerRequestData:
    player_id: int
    name: str
    country_code: str
    is_hidden: bool
    is_shadow: bool
    is_banned: bool
    discord_id: str | None

@dataclass
class PlayerFilter:
    name: str | None = None
    friend_code: str | None = None
    game: Game | None = None
    country: str | None = None
    is_hidden: bool | None = None
    is_shadow: bool | None = None
    is_banned: bool | None = None
    discord_id: str | None = None

@dataclass
class CreateSquadRequestData:
    squad_color: str
    squad_name: str | None
    squad_tag: str | None
    mii_name: str | None
    can_host: bool
    selected_fc_id: int | None

@dataclass
class ForceCreateSquadRequestData(CreateSquadRequestData):
    player_id: int
    roster_ids: List[int]
    representative_ids: List[int]

@dataclass
class RegisterTeamRequestData:
    squad_color: str
    squad_name: str
    squad_tag: str
    captain_player: int
    roster_ids: List[int]
    representative_ids: List[int]
    

@dataclass
class EditSquadRequestData:
    squad_id: int
    squad_name: str
    squad_tag: str
    squad_color: str
    is_registered: bool

# actually used for both inviting and kicking players from squads
@dataclass
class InvitePlayerRequestData:
    squad_id: int
    player_id: int
    is_representative: bool = False

@dataclass
class RegisterPlayerRequestData:
    mii_name: str | None
    can_host: bool
    selected_fc_id: int | None

@dataclass
class ForceRegisterPlayerRequestData(RegisterPlayerRequestData):
    squad_id: int | None
    player_id: int
    is_squad_captain: bool
    is_invite: bool
    is_checked_in: bool
    is_representative: bool

@dataclass
class EditPlayerRegistrationRequestData():
    player_id: int
    squad_id: int | None
    is_squad_captain: bool
    is_invite: bool
    is_checked_in: bool
    can_host: bool
    mii_name: str | None
    selected_fc_id: int | None
    is_representative: bool

@dataclass
class AcceptInviteRequestData():
    squad_id: int
    mii_name: str | None
    can_host: bool
    selected_fc_id: int | None

@dataclass
class DeclineInviteRequestData():
    squad_id: int

@dataclass
class UnregisterPlayerRequestData():
    squad_id: int | None

@dataclass
class StaffUnregisterPlayerRequestData():
    squad_id: int | None
    player_id: int

@dataclass
class TournamentPlayerDetails():
    player_id: int
    timestamp: int
    is_checked_in: bool
    mii_name: str | None
    can_host: bool
    name: str
    country_code: str | None
    discord_id: str | None
    friend_codes: List[str]

@dataclass
class SquadPlayerDetails(TournamentPlayerDetails):
    is_squad_captain: int
    is_invite: bool

@dataclass
class TournamentSquadDetails():
    id: int
    name: str | None
    tag: str | None
    color: int
    timestamp: int
    is_registered: int
    players: List[TournamentPlayerDetails]

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
    game: Game
    mode: GameMode
    date_start: int
    date_end: int

@dataclass
class TournamentDataBasic(TournamentDataMinimal):
    series_id: int | None
    is_squad: bool
    registrations_open: bool
    description: str
    logo: str

@dataclass
class TournamentFilter():
    is_minimal: bool = True
    name: str | None = None
    game: Game | None = None
    mode: GameMode | None = None
    series_id: int | None = None
    is_viewable: bool | None = None
    is_public: bool | None = None

@dataclass
class SeriesRequestData():
    series_name: str
    url: str | None
    game: Game
    mode: GameMode
    is_historical: bool
    is_public: bool
    description: str
    logo: str | None
    ruleset: str
    organizer: str
    location: str
    
@dataclass
class Series():
    id: int
    series_name: str
    url: str | None
    game: Game
    mode: GameMode
    is_historical: bool
    is_public: bool
    description: str
    logo: str | None

@dataclass
class SeriesFilter():
    is_historical: bool | None = None
    is_public: bool | None = None
    game: Game | None = None
    mode: GameMode | None = None

@dataclass
class TournamentTemplateRequestData(CreateTournamentRequestData):
    template_name: str

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

@dataclass
class RequestCreateTeamRequestData():
    name: str
    tag: str
    description: str
    language: str
    color: int
    logo: str | None
    game: Game
    mode: GameMode
    is_recruiting: bool

@dataclass
class CreateTeamRequestData(RequestCreateTeamRequestData):
    approval_status: Approval
    is_historical: bool
    is_active: bool

@dataclass
class EditTeamRequestData():
    team_id: int
    name: str
    tag: str
    description: str
    language: str
    color: int
    logo: str | None
    approval_status: Approval
    is_historical: bool

@dataclass
class ManagerEditTeamRequestData():
    team_id: int
    description: str
    language: str
    color: int
    logo: str | None

@dataclass
class RequestEditTeamRequestData():
    team_id: int
    name: str
    tag: str

@dataclass
class PartialTeamMember():
    player_id: int
    roster_id: int
    join_date: int

@dataclass
class PartialPlayer():
    player_id: int
    name: str
    country_code: str
    is_banned: bool
    discord_id: str
    friend_codes: List[str]

@dataclass
class RosterPlayerInfo():
    player_id: int
    name: str
    country_code: str
    is_banned: bool
    discord_id: str
    join_date: int
    friend_codes: List[FriendCode]
    
@dataclass
class TeamRoster():
    id: int
    team_id: int
    game: Game
    mode: GameMode
    name: str
    tag: str
    creation_date: int
    is_recruiting: bool
    is_approved: bool
    players: List[RosterPlayerInfo]

@dataclass
class Team():
    id: int
    name: str
    tag: str
    description: str
    creation_date: int
    language: str
    color: int
    logo: str | None
    is_approved: bool
    is_historical: bool
    rosters: List[TeamRoster]


@dataclass
class CreateRosterRequestData():
    team_id: int
    game: Game
    mode: GameMode
    name: str | None
    tag: str | None
    is_recruiting: bool
    is_active: bool
    approval_status: Approval

@dataclass
class EditRosterRequestData():
    roster_id: int
    team_id: int
    name: str | None
    tag: str | None
    is_recruiting: bool
    is_active: bool
    approval_status: Approval

@dataclass
class InviteRosterPlayerRequestData():
    team_id: int
    player_id: int
    roster_id: int

@dataclass
class AcceptRosterInviteRequestData():
    invite_id: int
    roster_leave_id: int | None

@dataclass
class DeclineRosterInviteRequestData():
    invite_id: int

@dataclass
class LeaveRosterRequestData():
    roster_id: int

@dataclass
class ApproveTransferRequestData():
    invite_id: int


@dataclass
class UserSettings:
    user_id: int
    avatar: str | None = None
    discord_tag: str | None = None
    about_me: str | None = None
    language: str = 'en-us'
    color_scheme: str = 'light'
    timezone: str = 'UTC'

@dataclass
class EditUserSettingsRequestData:
    avatar: str | None = None
    discord_tag: str | None = None
    about_me: str | None = None
    language: Literal['de', 'en-gb', 'en-us', 'es', 'fr', 'ja'] | None = None
    color_scheme: Literal['light', 'dark'] | None = None
    timezone: str | None = None

@dataclass
class Notification:
    id: int
    type: int
    content: str
    created_date: int
    is_read: bool

@dataclass
class NotificationFilter:
    is_read: Literal['0', '1'] | None = None
    type: str | None = None # separate multiple types with commas
    before: str | None = None
    after: str | None = None

@dataclass
class MarkAsReadRequestData:
    is_read: bool

@dataclass
class CreateFriendCodeRequestData:
    fc: str
    game: Game
    is_primary: bool
    description: str | None

@dataclass
class EditFriendCodeRequestData:
    id: int
    fc: str
    game: Game
    is_active: bool
    description: str | None

@dataclass
class EditPrimaryFriendCodeRequestData:
    id: int

@dataclass
class ModEditPrimaryFriendCodeRequestData(EditPrimaryFriendCodeRequestData):
    player_id: int

@dataclass
class DenyTransferRequestData():
    invite_id: int
    send_back: bool

@dataclass
class ApproveTeamEditRequestData():
    request_id: int

@dataclass
class DenyTeamEditRequestData():
    request_id: int

@dataclass
class RequestEditRosterRequestData():
    roster_id: int
    team_id: int
    name: str | None
    tag: str | None

@dataclass
class ApproveRosterEditRequestData():
    request_id: int

@dataclass
class DenyRosterEditRequestData():
    request_id: int

@dataclass
class ForceTransferPlayerRequestData():
    player_id: int
    roster_id: int
    team_id: int
    roster_leave_id: int | None

@dataclass
class EditTeamMemberInfoRequestData():
    id: int
    roster_id: int
    team_id: int
    join_date: int | None
    leave_date: int | None

@dataclass
class KickPlayerRequestData():
    id: int
    roster_id: int
    team_id: int