from dataclasses import dataclass

from common.data.models.common import FriendCodeType, CountryCode, Approval
from common.data.models.friend_codes import FriendCode, CreateFriendCodeRequestData
from common.data.models.user_settings import UserSettings
from common.data.models.player_bans import PlayerBanBasic
from common.data.models.discord_integration import Discord
from common.data.models.player_basic import PlayerBasic
    
@dataclass
class Player:
    id: int
    name: str
    country_code: CountryCode
    is_hidden: bool
    is_shadow: bool
    is_banned: bool
    join_date: int
    discord: Discord | None
    
@dataclass
class PlayerAndFriendCodes(Player):
    friend_codes: list[FriendCode]

@dataclass
class PlayerRoster:
    roster_id: int
    join_date: int
    team_id: int
    team_name: str
    team_tag: str
    team_color: int
    roster_name: str | None
    roster_tag: str | None
    game: str
    mode: str
    is_bagger_clause: bool

@dataclass
class PlayerTransferItem:
    team_id: int
    team_name: str
    game: str
    mode: str
    join_date: int
    leave_date: int | None
    roster_name: str

@dataclass
class PlayerTransferHistory:
    history: list[PlayerTransferItem]

@dataclass
class PlayerNameChange:
    id: int
    old_name: str
    new_name: str
    date: int
    approval_status: Approval

@dataclass
class PlayerNotes:
    notes: str
    edited_by: Player | None
    date: int

@dataclass
class PlayerRole:
    id: int
    name: str
    position: int

@dataclass
class PlayerDetailed(PlayerAndFriendCodes):
    rosters: list[PlayerRoster]
    ban_info: PlayerBanBasic | None
    user_settings: UserSettings | None
    name_changes: list[PlayerNameChange]
    notes: PlayerNotes | None
    roles: list[PlayerRole]

@dataclass
class PlayerList:
    player_list: list[PlayerDetailed]
    player_count: int
    page_count: int

@dataclass
class CreatePlayerRequestData:
    name: str
    country_code: CountryCode
    friend_codes: list[CreateFriendCodeRequestData]
    is_hidden: bool = False
    is_shadow: bool = False
    

@dataclass
class EditPlayerRequestData:
    player_id: int
    name: str
    country_code: CountryCode
    is_hidden: bool
    is_shadow: bool

@dataclass
class PlayerFilter:
    name: str | None = None
    friend_code: str | None = None
    name_or_fc: str | None = None
    fc_type: FriendCodeType | None = None
    country: CountryCode | None = None
    is_hidden: bool | None = None
    is_shadow: bool | None = None
    is_banned: bool | None = None
    discord_id: str | None = None
    detailed: bool | None = None
    page: int | None = None
    squad_id: int | None = None
    matching_fcs_only: bool = False
    include_shadow_players: bool = False
    sort_by_newest: bool | None = False

@dataclass
class PlayerRequestNameRequestData:
    name: str

@dataclass
class PlayerNameRequest:
    id: int
    player_id: int
    player_country: CountryCode
    old_name: str
    new_name: str
    date: int
    approval_status: Approval
    handled_by: PlayerBasic | None

@dataclass
class PlayerNameRequestFilter:
    approval_status: Approval
    page: int | None = None

@dataclass
class PlayerNameRequestList:
    change_list: list[PlayerNameRequest]
    count: int
    page_count: int

@dataclass
class ApprovePlayerNameRequestData:
    request_id: int

@dataclass
class UpdatePlayerNotesRequestData:
    notes: str

@dataclass
class ClaimPlayerRequestData:
    player_id: int

@dataclass
class ApproveDenyPlayerClaimRequestData:
    claim_id: int

@dataclass
class PlayerClaim:
    id: int
    date: int
    approval_status: Approval
    player: PlayerBasic
    claimed_player: PlayerBasic

@dataclass
class MergePlayersRequestData:
    from_player_id: int
    to_player_id: int
@dataclass
class PlayerMin:
    id: int
    name: str

