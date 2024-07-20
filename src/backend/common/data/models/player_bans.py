from dataclasses import dataclass

@dataclass
class PlayerBan:
    player_id: int
    banned_by: int
    is_indefinite: bool
    ban_date: int
    expiration_date: int
    reason: str

@dataclass
class PlayerBanHistorical(PlayerBan):
    unbanned_by: int | None = None

@dataclass
class PlayerBanRequestData:
    is_indefinite: bool
    expiration_date: int
    reason: str

@dataclass
class PlayerBanFilter:
    player_id: int | None = None
    banned_by: int | None = None
    is_indefinite: bool | None = None
    expires_before: int | None = None
    expires_after: int | None = None
    banned_before: int | None = None
    banned_after: int | None = None
    reason: str | None = None
    page: int | None = None

@dataclass
class PlayerBanHistoricalFilter(PlayerBanFilter):
    unbanned_by: int | None = None

@dataclass
class PlayerBanList:
    ban_list: list[PlayerBan]
    ban_count: int
    page_count: int

@dataclass
class PlayerBanHistoricalList:
    ban_list: list[PlayerBanHistorical]
    ban_count: int
    page_count: int