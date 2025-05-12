from dataclasses import dataclass
from common.data.db.common import IndexModel


@dataclass
class SessionsUserId(IndexModel):
    @staticmethod
    def get_create_index_command() -> str:
        return """CREATE INDEX IF NOT EXISTS idx_sessions_user_id
            ON sessions(user_id)"""


@dataclass
class SessionsExpiresOn(IndexModel):
    @staticmethod
    def get_create_index_command() -> str:
        return """CREATE INDEX IF NOT EXISTS idx_sessions_expires_on
            ON sessions(expires_on)"""


all_indices: list[type[IndexModel]] = [
    SessionsUserId,
    SessionsExpiresOn
]
