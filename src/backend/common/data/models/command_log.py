from dataclasses import dataclass
from datetime import datetime

@dataclass
class CommandLog[T]:
    id: int
    type: str
    command: T
    timestamp: int


@dataclass
class HistoricalCommandLogIndexEntry:
    file_name: str
    from_id: int
    from_time: datetime