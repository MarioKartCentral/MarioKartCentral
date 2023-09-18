from dataclasses import dataclass
from typing import List, Literal

@dataclass
class Record:
    id: int
    version: int
    player_id: int
    set_time: str
    updated_time: str
    game: str
    type: str
    time: str | None = None 
    time_ms: float | None = None 
    cc: int | None = None
    course: str | None = None

@dataclass
class RecordFilter:
    game: str | None  = None
    type: str | None = None
    cc: str | None  = None
    course: str | None = None
    country: str | None = None
    player_id: int | Literal["*"] | None = None

@dataclass
class RecordCacheEntryPlayer:
    id: int
    name: str
    country: str | None

@dataclass
class RecordCacheEntry:
    id: int
    version: int
    player: RecordCacheEntryPlayer | None
    game: str | None
    type: str | None
    time: str | None = None 
    time_ms: float | None = None 
    cc: int | None = None
    course: str | None = None

@dataclass
class RecordCache:
    filter: RecordFilter # 
    last_updated: str # ISO 8601 UTC timestamp
    records: List[RecordCacheEntry]