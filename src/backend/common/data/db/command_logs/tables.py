from dataclasses import dataclass
from common.data.db.common import TableModel


@dataclass
class CommandLog(TableModel):
    id: int
    type: str
    data: str
    timestamp: int

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS command_log(
        id INTEGER PRIMARY KEY autoincrement,
        type TEXT NOT NULL,
        data TEXT NOT NULL,
        timestamp INTEGER NOT NULL DEFAULT (cast(strftime('%s','now') as int)))"""


all_tables : list[type[TableModel]] = [
    CommandLog
]
