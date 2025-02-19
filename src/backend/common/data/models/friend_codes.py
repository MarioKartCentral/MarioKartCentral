from dataclasses import dataclass

from common.data.models.common import FriendCodeType
from common.data.models.player_basic import PlayerBasic

@dataclass
class FriendCode:
    id: int
    fc: str
    type: FriendCodeType
    player_id: int
    is_verified: bool
    is_primary: bool
    creation_date: int
    description: str | None = None
    is_active: bool = True

@dataclass
class CreateFriendCodeRequestData:
    fc: str
    type: FriendCodeType
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

@dataclass
class FriendCodeEditFilter:
    page: int | None = None

@dataclass
class FriendCodeEdit:
    id: int
    old_fc: str | None
    new_fc: str | None
    is_active: bool | None
    date: int
    fc: FriendCode
    player: PlayerBasic
    handled_by: PlayerBasic | None

@dataclass
class FriendCodeEditList:
    change_list: list[FriendCodeEdit]
    count: int
    page_count: int