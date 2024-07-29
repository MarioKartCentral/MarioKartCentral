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
class PlayerBanDetailed:
    player_name: str
    player_id: int
    player_country_code: str
    is_indefinite: bool
    ban_date: int
    expiration_date: int
    reason: str
    banned_by_uid: int
    banned_by_pid: int
    banned_by_name: str | None = None
    unban_date: int | None = None
    unbanned_by_uid: int | None = None
    unbanned_by_pid: int | None = None
    unbanned_by_name: str | None = None

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
    unbanned_before: int | None = None
    unbanned_after: int | None = None

@dataclass
class PlayerBanList:
    ban_list: list[PlayerBanDetailed]
    ban_count: int
    page_count: int
