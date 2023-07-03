from dataclasses import dataclass


@dataclass
class User:
    id: int
    player_id: int | None

@dataclass
class UserPlayer:
    id: int
    player_id: int | None
    name: str | None
    country_code: str | None
    is_hidden: bool | None
    is_shadow: bool | None
    is_banned: bool | None
    discord_id: str | None

@dataclass
class UserLoginData(User):
    email: str
    password_hash: str