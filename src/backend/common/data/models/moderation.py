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
    countryCode: str | None = None

@dataclass
class AltFlagFilter:
    page: int | None = None

@dataclass
class PlayerAltFlagRequestData:
    player_id: int

@dataclass
class AltFlagUser:
    user_id: int
    player: PlayerBasic | None

@dataclass
class AltFlag:
    id: int
    type: str
    flag_key: str
    data: str
    score: int
    date: int
    fingerprint_hash: str | None
    users: list[AltFlagUser]

@dataclass
class AltFlagList:
    flags: list[AltFlag]
    count: int
    page_count: int