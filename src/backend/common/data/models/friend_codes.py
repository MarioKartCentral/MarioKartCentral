from dataclasses import dataclass
from common.data.validators import validate_game

@dataclass
class FriendCode:
    fc: str
    game: str
    player_id: int
    is_verified: int
    is_primary: int
    description: str | None = None

    def __post_init__(self):
        validate_game(self.game)

@dataclass
class CreateFriendCodeRequestData:
    fc: str
    game: str
    is_primary: bool
    description: str | None

    def __post_init__(self):
        validate_game(self.game)

@dataclass
class EditFriendCodeRequestData:
    id: int
    fc: str
    game: str
    is_active: bool
    description: str | None

    def __post_init__(self):
        validate_game(self.game)

@dataclass
class EditPrimaryFriendCodeRequestData:
    id: int

@dataclass
class ModEditPrimaryFriendCodeRequestData(EditPrimaryFriendCodeRequestData):
    player_id: int