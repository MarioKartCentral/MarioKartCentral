from dataclasses import dataclass
from common.config.common import load_config

@dataclass
class RecordDataTypeAttribute[T]:
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

record_config = load_config("records.json", RecordData)