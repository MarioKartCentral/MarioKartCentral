from dataclasses import dataclass
from common.data.db.common import TableModel


@dataclass
class AltFlag(TableModel):
    id: int
    type: str
    data: str
    score: int
    date: int
    login_id: int | None

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS alt_flags(
            id INTEGER PRIMARY KEY,
            type TEXT NOT NULL,
            data TEXT NOT NULL,
            score INTEGER NOT NULL,
            date INTEGER NOT NULL,
            login_id INTEGER
        )"""
    
@dataclass
class UserAltFlag(TableModel):
    user_id: int
    flag_id: int

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS user_alt_flags(
            user_id INTEGER NOT NULL,
            flag_id INTEGER NOT NULL REFERENCES alt_flags(id),
            PRIMARY KEY (user_id, flag_id)) WITHOUT ROWID"""


all_tables : list[type[TableModel]] = [
    AltFlag, UserAltFlag
]
