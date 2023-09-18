from dataclasses import dataclass
from typing import Literal

from common.data.models.friend_codes import FriendCode, CreateFriendCodeRequestData
from common.data.models.user_settings import UserSettings
from common.data.validators import validate_country_code, validate_game

    
@dataclass
class Player:
    id: int
    name: str
    country_code: str
    is_hidden: bool
    is_shadow: bool
    is_banned: bool
    discord_id: str | None

    def __post_init__(self):
        validate_country_code(self.country_code)

@dataclass
class PlayerBan:
    player_id: int
    staff_id: int
    is_indefinite: bool
    expiration_date: int
    reason: str

@dataclass
class PlayerDetailed(Player):
    friend_codes: list[FriendCode]
    ban_info: PlayerBan | None
    user_settings: UserSettings | None

@dataclass
class CreatePlayerRequestData:
    name: str
    country_code: str
    friend_codes: list[CreateFriendCodeRequestData]
    is_hidden: bool = False
    is_shadow: bool = False
    discord_id: str | None = None

    def __post_init__(self):
        validate_country_code(self.country_code)
    

@dataclass
class EditPlayerRequestData:
    player_id: int
    name: str
    country_code: str
    is_hidden: bool
    is_shadow: bool
    discord_id: str | None

    def __post_init__(self):
        validate_country_code(self.country_code)

@dataclass
class PlayerFilter:
    name: str | None = None
    friend_code: str | None = None
    game: str | None = None
    country: str | None = None
    is_hidden: bool | None = None
    is_shadow: bool | None = None
    is_banned: bool | None = None
    discord_id: str | None = None

    def __post_init__(self):
        if self.game is not None:
            validate_game(self.game)

        if self.country is not None:
            validate_country_code(self.country)

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
