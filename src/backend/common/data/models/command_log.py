from dataclasses import dataclass
from datetime import datetime
from typing import Generic, TypeVar

_TCommand = TypeVar('_TCommand')

@dataclass
class CommandLog(Generic[_TCommand]):
    id: int
    type: str
    command: _TCommand
    timestamp: int


@dataclass
class HistoricalCommandLogIndexEntry:
    file_name: str
    from_id: int
    from_time: datetime