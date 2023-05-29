from dataclasses import dataclass

from common.data.models.common import Game

@dataclass
class FriendCode:
    fc: str
    game: Game
    player_id: int
    is_verified: int
    is_primary: int

@dataclass
class CreateFriendCodeRequestData:
    fc: str
    game: Game
    is_primary: bool
    description: str | None

@dataclass
class EditFriendCodeRequestData:
    id: int
    fc: str
    game: Game
    is_active: bool
    description: str | None

@dataclass
class EditPrimaryFriendCodeRequestData:
    id: int

@dataclass
class ModEditPrimaryFriendCodeRequestData(EditPrimaryFriendCodeRequestData):
    player_id: int