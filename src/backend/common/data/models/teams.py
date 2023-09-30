from dataclasses import dataclass
from common.data.models.common import Approval, Game, GameMode
from common.data.models.friend_codes import FriendCode
from common.data.models.players import Player


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
class TeamEditRequest():
    id: int
    team_id: int
    old_name: str
    old_tag: str
    new_name: str
    new_tag: str
    date: int
    approval_status: Approval

@dataclass
class RosterEditRequest():
    id: int
    roster_id: int
    team_id: int
    team_name: str
    team_tag: str
    old_name: str | None
    old_tag: str | None
    new_name: str | None
    new_tag: str | None
    date: int
    approval_status: Approval

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
class RosterInvitedPlayer():
    player_id: int
    name: str
    country_code: str
    is_banned: bool
    discord_id: str
    invite_date: int
    friend_codes: list[FriendCode]
    
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
    players: list[RosterPlayerInfo]
    invites: list[RosterInvitedPlayer]

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
class RequestCreateRosterRequestData():
    team_id: int
    game: Game
    mode: GameMode
    name: str | None
    tag: str | None
    is_recruiting: bool

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
    player_id: int
    roster_id: int
    team_id: int
    join_date: int | None
    leave_date: int | None

@dataclass
class KickPlayerRequestData():
    player_id: int
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

@dataclass
class TeamInvite():
    invite_id: int
    date: int
    team_id: int
    team_name: str
    team_tag: str
    team_color: int
    roster_id: int
    roster_name: str | None
    roster_tag: str | None
    game: Game
    mode: GameMode

@dataclass
class LeaveRoster():
    team_id: int
    team_name: str
    team_tag: str
    team_color: int
    roster_id: int
    roster_name: str | None
    roster_tag: str | None

@dataclass
class TeamInviteApproval(TeamInvite):
    player_id: int
    player_name: str
    player_country_code: str
    roster_leave_id: int | None
    roster_leave: LeaveRoster | None

@dataclass
class RequestRosterChangeRequestData():
    roster_id: int
    team_id: int
    name: str | None
    tag: str | None

@dataclass
class EditRosterChangeRequestData():
    request_id: int

@dataclass
class ManagerEditRosterRequestData():
    roster_id: int
    team_id: int
    is_recruiting: bool