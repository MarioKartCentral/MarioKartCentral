from dataclasses import dataclass
from typing import Literal

@dataclass
class PlayerBan:
    player_id: int
    staff_id: int
    is_indefinite: bool
    ban_date: int
    expiration_date: int
    reason: str

@dataclass
class PlayerBanRequestData:
    is_indefinite: bool
    expiration_date: int
    reason: str

@dataclass
class PlayerBanFilter:
    player_id: str | None = None
    staff_id: str | None = None
    is_indefinite: Literal['0', '1'] | None = None
    expires_before: str | None = None
    expires_after: str | None = None
    banned_before: str | None = None
    banned_after: str | None = None
    reason: str | None = None
    page: int | None = None
    is_historical: Literal['0', '1'] | None = None

@dataclass
class PlayerBanList:
    ban_list: list[PlayerBan]
    ban_count: int
    page_count: int