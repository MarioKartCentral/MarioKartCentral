from dataclasses import dataclass
from typing import Generic, TypeVar
from common.config.common import load_config
from common.data.models import RecordFilter

T = TypeVar('T')

@dataclass
class RecordDataTypeAttribute(Generic[T]):
    required: bool = False
    values: T | None = None

@dataclass
class RecordDataType:
    course: RecordDataTypeAttribute[str] | None
    cc: RecordDataTypeAttribute[int] | None

@dataclass
class RecordDataGame:
    types: dict[str, RecordDataType]

@dataclass
class RecordData:
    games: dict[str, RecordDataGame]
    caches: list[RecordFilter]

record_data = load_config("records.json", RecordData)