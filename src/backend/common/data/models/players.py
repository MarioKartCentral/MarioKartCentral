from dataclasses import dataclass

from common.data.models.common import Game, CountryCode
from common.data.models.friend_codes import FriendCode, CreateFriendCodeRequestData
from common.data.models.user_settings import UserSettings
from common.data.models.player_bans import PlayerBanBasic

    
@dataclass
class Player:
    id: int
    name: str
    country_code: CountryCode
    is_hidden: bool
    is_shadow: bool
    is_banned: bool
    discord_id: str | None
    
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

@dataclass
class PlayerDetailed(PlayerAndFriendCodes):
    rosters: list[PlayerRoster]
    ban_info: PlayerBanBasic | None
    user_settings: UserSettings | None

@dataclass
class PlayerList:
    player_list: list[PlayerAndFriendCodes]
    player_count: int
    page_count: int

@dataclass
class CreatePlayerRequestData:
    name: str
    country_code: CountryCode
    friend_codes: list[CreateFriendCodeRequestData]
    is_hidden: bool = False
    is_shadow: bool = False
    discord_id: str | None = None
    

@dataclass
class EditPlayerRequestData:
    player_id: int
    name: str
    country_code: CountryCode
    is_hidden: bool
    is_shadow: bool
    discord_id: str | None

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
