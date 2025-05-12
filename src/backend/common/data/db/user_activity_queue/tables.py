from dataclasses import dataclass
from typing import List, Type
from common.data.db.common import TableModel

@dataclass
class UserActivityQueue(TableModel):
    id: int
    user_id: int
    ip_address: str
    path: str
    referer: str | None
    timestamp: int

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS user_activity_queue(
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            ip_address TEXT NOT NULL,
            path TEXT NOT NULL,
            referer TEXT,
            timestamp INTEGER NOT NULL
        )"""

all_tables: List[Type[TableModel]] = [UserActivityQueue]
