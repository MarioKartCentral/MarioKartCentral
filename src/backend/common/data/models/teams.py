from dataclasses import dataclass
from common.data.models.common import Approval
from common.data.models.friend_codes import FriendCode
from common.data.models.players import Player
from common.data.validators import validate_game_and_mode


@dataclass
class RequestCreateTeamRequestData():
    name: str
    tag: str
    description: str
    language: str
    color: int
    logo: str | None
    game: str
    mode: str
    is_recruiting: bool

    def __post_init__(self):
        validate_game_and_mode(self.game, self.mode)

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
    friend_codes: list[FriendCode]

@dataclass
class RosterPlayerInfo():
    player_id: int
    name: str
    country_code: str
    is_banned: bool
    discord_id: str
    join_date: int
    friend_codes: list[FriendCode]
    
@dataclass
class TeamRoster():
    id: int
    team_id: int
    game: str
    mode: str
    name: str
    tag: str
    creation_date: int
    is_recruiting: bool
    is_approved: bool
    players: list[RosterPlayerInfo]

    def __post_init__(self):
        validate_game_and_mode(self.game, self.mode)

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
    rosters: list[TeamRoster]
    managers: list[Player]


@dataclass
class CreateRosterRequestData():
    team_id: int
    game: str
    mode: str
    name: str | None
    tag: str | None
    is_recruiting: bool
    is_active: bool
    approval_status: Approval

    def __post_init__(self):
        validate_game_and_mode(self.game, self.mode)

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

@dataclass
class TeamFilter():
    name: str | None = None
    tag: str | None = None
    game: str | None = None
    mode: str | None = None
    language: str | None = None
    is_recruiting: bool | None = None
    is_historical: bool | None = None

    def __post_init__(self):
        if self.game is not None and self.mode is not None:
            validate_game_and_mode(self.game, self.mode)

