from dataclasses import dataclass
from common.data.db.common import TableModel


@dataclass
class PlayerNotes(TableModel):
    player_id: int
    notes: str
    edited_by: int
    date: int

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS player_notes (
            player_id INTEGER PRIMARY KEY,
            notes TEXT NOT NULL,
            edited_by INTEGER NOT NULL,
            date INTEGER NOT NULL
            )"""


all_tables : list[type[TableModel]] = [
    PlayerNotes
]
