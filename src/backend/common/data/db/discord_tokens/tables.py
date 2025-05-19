from dataclasses import dataclass
from common.data.db.common import TableModel

@dataclass
class DiscordToken(TableModel):
    user_id: int
    access_token: str
    token_expires_on: int
    refresh_token: str

    @staticmethod
    def get_create_table_command():
        return """CREATE TABLE IF NOT EXISTS discord_tokens(
            user_id INTEGER PRIMARY KEY NOT NULL,
            access_token TEXT NOT NULL,
            token_expires_on INTEGER NOT NULL,
            refresh_token TEXT NOT NULL) WITHOUT ROWID"""

all_tables : list[type[TableModel]] = [DiscordToken]
