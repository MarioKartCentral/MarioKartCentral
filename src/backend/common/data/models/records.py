from dataclasses import dataclass

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
    cc: str | None = None
    course: str | None = None

@dataclass
class RecordPlayerData:
    id: int
    name: str
    country: str | None

@dataclass
class RecordMetadata:
    id: int
    version: int
    player_id: int
    url: str

@dataclass
class PlayerRecordListMetadata:
    player: RecordPlayerData
    url: str | None # None if there are no records by this player
    updated_records: list[Record]

@dataclass
class CategoryRecordListMetadata:
    url: str | None # None if there are no records in this category
    updated_players: list[RecordPlayerData]
    updated_records: list[Record]

@dataclass
class RecordCacheUpdates:
    """This class contains information about changes that need to be applied to a record cache"""
    records: list[Record]
    players: list[RecordPlayerData]

@dataclass
class RecordCategory:
    game: str
    type: str
    cc: str = 'None'
    course: str = 'None'

@dataclass
class CategoryRecordCache:
    category: RecordCategory
    players: list[RecordPlayerData]
    records: list[Record]

@dataclass
class PlayerRecordCache:
    player: RecordPlayerData
    records: list[Record]

