from dataclasses import dataclass
from common.data.models.player_basic import PlayerBasic
from typing import Literal

@dataclass
class FilteredWords:
    words: list[str]

@dataclass
class IPInfoBasic:
    user_id: int
    ip_address: str

@dataclass
class IPCheckResponse:
    status: Literal["success", "fail"]
    message: str | None = None
    mobile: bool = False
    proxy: bool = False

@dataclass
class AltFlagFilter:
    page: int | None = None

@dataclass
class PlayerAltFlagRequestData:
    player_id: int

@dataclass
class AltFlag:
    id: int
    type: str
    data: str
    score: int
    date: int
    fingerprint_hash: str | None
    players: list[PlayerBasic]

@dataclass
class AltFlagList:
    flags: list[AltFlag]
    count: int
    page_count: int