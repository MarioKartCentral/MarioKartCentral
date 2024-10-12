from dataclasses import dataclass

from common.data.models.common import Game, CountryCode
from common.data.models.friend_codes import FriendCode, CreateFriendCodeRequestData
from common.data.models.user_settings import UserSettings
from common.data.models.player_bans import PlayerBanBasic
from common.data.models.discord_integration import Discord

    
@dataclass
class Player:
    id: int
    name: str
    country_code: CountryCode
    is_hidden: bool
    is_shadow: bool
    is_banned: bool
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
class PlayerDetailed(PlayerAndFriendCodes):
    rosters: list[PlayerRoster]
    ban_info: PlayerBanBasic | None
    user_settings: UserSettings | None

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
    game: Game | None = None
    country: CountryCode | None = None
    is_hidden: bool | None = None
    is_shadow: bool | None = None
    is_banned: bool | None = None
    discord_id: str | None = None
    detailed: bool | None = None
    page: int | None = None
    squad_id: int | None = None
    matching_fcs_only: bool = False

@dataclass
class PlayerBanRequestData:
    is_indefinite: bool
    expiration_date: int
    reason: str

@dataclass
class PlayerBanFilter:
    player_id: str | None = None
    staff_id: str | None = None
    is_indefinite: Literal['0', '1'] | None = None
    expires_before: str | None = None
    expires_after: str | None = None
    reason: str | None = None