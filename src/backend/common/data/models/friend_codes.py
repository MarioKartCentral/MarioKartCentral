from dataclasses import dataclass

from common.data.models.common import Game

@dataclass
class FriendCode:
    id: int
    fc: str
    game: Game
    player_id: int
    is_verified: bool
    is_primary: bool
    description: str | None = None
    is_active: bool = True

@dataclass
class CreateFriendCodeRequestData:
    fc: str
    game: Game
    is_primary: bool
    description: str | None

@dataclass
class ForceCreateFriendCodeRequestData(CreateFriendCodeRequestData):
    player_id: int

@dataclass
class EditMyFriendCodeRequestData:
    id: int
    is_primary: bool
    description: str | None

@dataclass
class ForceEditFriendCodeRequestData(EditMyFriendCodeRequestData):
    player_id: int
    fc: str
    is_active: bool

@dataclass
class EditPrimaryFriendCodeRequestData:
    id: int

@dataclass
class ModEditPrimaryFriendCodeRequestData(EditPrimaryFriendCodeRequestData):
    player_id: int