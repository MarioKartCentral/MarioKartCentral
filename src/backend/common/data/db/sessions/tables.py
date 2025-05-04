from dataclasses import dataclass
from common.data.db.common import TableModel

@dataclass
class Session(TableModel):
    session_id: str
    user_id: int
    expires_on: int

    @staticmethod
    def get_create_table_command():
        return """CREATE TABLE IF NOT EXISTS sessions(
            session_id TEXT PRIMARY KEY NOT NULL,
            user_id INTEGER NOT NULL,
            expires_on INTEGER NOT NULL) WITHOUT ROWID"""

all_tables : list[type[TableModel]] = [Session]