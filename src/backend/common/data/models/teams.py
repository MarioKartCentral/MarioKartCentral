from dataclasses import dataclass
from common.data.models.common import Approval, Game, GameMode
from common.data.models.friend_codes import FriendCode
from common.data.models.players import Player
from common.data.models.discord_integration import Discord


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

# @dataclass
# class CreateTeamRequestData(RequestCreateTeamRequestData):
#     approval_status: Approval
#     is_historical: bool
#     is_active: bool

@dataclass
class CreateTeamRequestData:
    name: str
    tag: str
    description: str
    language: str
    color: int
    logo: str | None
    game: Game
    mode: GameMode
    is_recruiting: bool
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
    color: int
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
    color: int
    date: int
    approval_status: Approval

@dataclass
class PartialTeamMember():
    player_id: int
    roster_id: int
    join_date: int
    is_bagger_clause: bool

@dataclass
class PartialPlayer():
    player_id: int
    name: str
    country_code: str
    is_banned: bool
    discord: Discord | None
    friend_codes: list[FriendCode]

@dataclass
class RosterPlayerInfo():
    player_id: int
    name: str
    country_code: str
    is_banned: bool
    discord: Discord | None
    join_date: int
    is_manager: bool
    is_leader: bool
    is_bagger_clause: bool
    friend_codes: list[FriendCode]

@dataclass
class RosterInvitedPlayer():
    player_id: int
    name: str
    country_code: str
    is_banned: bool
    discord: Discord | None
    invite_date: int
    is_bagger_clause: bool
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
    is_active: bool
    approval_status: Approval
    color: int
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
    approval_status: Approval
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
class DeleteInviteRequestData():
    team_id: int
    player_id: int
    roster_id: int

# @dataclass
# class InviteRosterPlayerRequestData(DeleteInviteRequestData):
#     is_bagger_clause: bool

@dataclass
class InviteRosterPlayerRequestData():
    team_id: int
    player_id: int
    roster_id: int
    is_bagger_clause: bool

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
    is_bagger_clause: bool

@dataclass
class EditTeamMemberInfoRequestData():
    player_id: int
    roster_id: int
    team_id: int
    join_date: int | None
    leave_date: int | None
    is_bagger_clause: bool

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
    is_bagger_clause: bool
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
class TransferRoster():
    team_id: int
    team_name: str
    team_tag: str
    team_color: int
    roster_id: int
    roster_name: str | None
    roster_tag: str | None

@dataclass
class TeamTransfer():
    invite_id: int
    date: int
    is_bagger_clause: bool
    game: Game
    mode: GameMode
    player_id: int
    player_name: str
    player_country_code: str
    approval_status: Approval
    roster_leave: TransferRoster | None
    roster_join: TransferRoster | None

@dataclass
class TransferFilter():
    game: Game | None = None
    mode: GameMode | None = None
    team_id: int | None = None
    roster_id: int | None = None
    from_date: int | None = None
    to_date: int | None = None
    page: int | None = None

@dataclass
class TransferList():
    transfers: list[TeamTransfer]
    transfer_count: int
    page_count: int

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

@dataclass
class RegisterableRostersRequestData():
    tournament_id: int
    game: Game
    mode: GameMode