from dataclasses import dataclass

from common.data.models.common import Game

@dataclass
class FriendCode:
    id: int
    fc: str
    game: Game
    player_id: int
    is_verified: int
    is_primary: int
    description: str | None = None
    is_active: bool = True

@dataclass
class CreateFriendCodeRequestData:
    fc: str
    game: Game
    is_primary: bool
    description: str | None

@dataclass
class ForceCreateFriendCodeRequestData:
    player_id: int
    fc: str
    game: Game
    is_primary: bool
    description: str | None

@dataclass
class EditMyFriendCodeRequestData:
    id: int
    is_primary: bool
    description: str | None

@dataclass
class ForceEditFriendCodeRequestData:
    player_id: int
    id: int
    fc: str
    is_primary: bool
    is_active: bool
    description: str | None

@dataclass
class EditPrimaryFriendCodeRequestData:
    id: int

# @dataclass
# class ModEditPrimaryFriendCodeRequestData(EditPrimaryFriendCodeRequestData):
#     player_id: int
@dataclass
class ModEditPrimaryFriendCodeRequestData:
    id: int
    player_id: int