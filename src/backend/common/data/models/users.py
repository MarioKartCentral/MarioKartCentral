from dataclasses import dataclass

from common.data.models.players import PlayerDetailed

@dataclass
class User:
    id: int
    player_id: int | None

@dataclass
class UserPlayer:
    id: int
    player_id: int | None
    player: PlayerDetailed | None
    permissions: list[str]

@dataclass
class UserLoginData(User):
    email: str
    password_hash: str

@dataclass
class PermissionsCheck:
    permissions: str | None = None