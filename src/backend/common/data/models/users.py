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

@dataclass
class UserLoginData(User):
    email: str
    password_hash: str