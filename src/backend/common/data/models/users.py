from dataclasses import dataclass

from common.data.models.players import PlayerDetailed

@dataclass
class User:
    id: int
    player_id: int | None

@dataclass
class ModNotifications:
    pending_teams: int = 0

@dataclass
class UserPlayer:
    id: int
    player_id: int | None
    player: PlayerDetailed | None
    permissions: list[str]
    mod_notifications: ModNotifications | None

@dataclass
class UserLoginData(User):
    email: str
    password_hash: str

@dataclass
class PermissionsCheck:
    permissions: str | None = None