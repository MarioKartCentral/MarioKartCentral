from dataclasses import dataclass
from typing import Any, Dict, List

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

@dataclass
class FriendCode:
    fc: str
    game: str
    player_id: int
    is_verified: int

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
    game: str | None = None
    country: str | None = None
    is_hidden: bool | None = None
    is_shadow: bool | None = None
    is_banned: bool | None = None
    discord_id: str | None = None

@dataclass
class CreateSquadRequestData:
    squad_color: str
    squad_name: str | None = None
    squad_tag: str | None = None
    mii_name: str | None = None
    can_host: bool = False

@dataclass
class ForceCreateSquadRequestData:
    player_id: int
    squad_color: str
    squad_name: str | None = None
    squad_tag: str | None = None
    mii_name: str | None = None
    can_host: bool = False

@dataclass
class EditSquadRequestData:
    squad_id: int
    squad_name: str
    squad_tag: str
    squad_color: str
    is_registered: bool