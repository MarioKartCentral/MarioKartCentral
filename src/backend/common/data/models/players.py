from dataclasses import dataclass
from typing import List, Literal

from common.data.models.common import Game, CountryCode
from common.data.models.friend_codes import FriendCode
from common.data.models.users import User

    
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
class PlayerDetailed(Player):
    friend_codes: List[FriendCode]
    user: User | None

@dataclass
class CreatePlayerRequestData:
    name: str
    country_code: CountryCode
    is_hidden: bool = False
    is_shadow: bool = False
    is_banned: bool = False
    discord_id: str | None = None

@dataclass
class EditPlayerRequestData:
    player_id: int
    name: str
    country_code: CountryCode
    is_hidden: bool
    is_shadow: bool
    is_banned: bool
    discord_id: str | None

@dataclass
class PlayerFilter:
    name: str | None = None
    friend_code: str | None = None
    game: Game | None = None
    country: CountryCode | None = None
    is_hidden: bool | None = None
    is_shadow: bool | None = None
    is_banned: bool | None = None
    discord_id: str | None = None

@dataclass
class PlayerBan:
    player_id: int
    staff_id: int
    is_indefinite: bool
    expiration_date: int
    reason: str

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
