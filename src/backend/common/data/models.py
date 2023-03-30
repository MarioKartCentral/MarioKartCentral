
from dataclasses import dataclass
from typing import Any, Dict, List

@dataclass
class Error:
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

@dataclass
class UserLoginData(User):
    email: str
    password_hash: str

@dataclass
class UserDetailed(User):
    player: 'Player'

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
class PlayerDetailed(Player):
    friend_codes: List[FriendCode]
    user: User | None