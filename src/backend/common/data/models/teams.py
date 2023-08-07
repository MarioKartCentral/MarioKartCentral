from dataclasses import dataclass
from typing import List

from common.data.models.common import Approval, Game, GameMode
from common.data.models.friend_codes import FriendCode


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
    game: Game | None = None
    mode: GameMode | None = None
    language: str | None = None
    is_recruiting: bool | None = None
    is_historical: bool | None = None

