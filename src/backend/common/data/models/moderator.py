from dataclasses import dataclass
from common.data.models.players import PlayerBasic

@dataclass
class SessionMatchFilter:
    page: int | None = None

@dataclass
class SessionMatchUser:
    user_id: int
    date_earliest: int
    date_latest: int
    player_info: PlayerBasic
    is_banned: bool

@dataclass
class SessionMatch:
    date: int
    users: list[SessionMatchUser]

@dataclass
class SessionMatchList:
    session_matches: list[SessionMatch]
    match_count: int
    page_count: int

@dataclass
class IPMatchFilter:
    page: int | None = None

@dataclass
class IPMatchUser:
    user_id: int
    date_earliest: int
    date_latest: int
    times: int
    player_info: PlayerBasic
    is_banned: bool

@dataclass
class IPMatch:
    ip_address: str | None
    date: int
    users: list[IPMatchUser]

@dataclass
class IPMatchList:
    ip_matches: list[IPMatch]
    match_count: int
    page_count: int