from dataclasses import dataclass
from ..common import TableModel

@dataclass
class UserAuth(TableModel):
    user_id: int
    email: str
    password_hash: str
    email_confirmed: bool
    force_password_reset: bool

    @staticmethod
    def get_create_table_command():
        return """CREATE TABLE IF NOT EXISTS user_auth(
            user_id INTEGER PRIMARY KEY NOT NULL,
            email TEXT COLLATE NOCASE UNIQUE,
            password_hash TEXT,
            email_confirmed BOOLEAN NOT NULL DEFAULT 0,
            force_password_reset BOOLEAN NOT NULL DEFAULT 0
            ) WITHOUT ROWID"""

@dataclass
class EmailVerification(TableModel):
    token_id: str
    user_id: int
    expires_on: int

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS email_verifications(
            token_id TEXT PRIMARY KEY NOT NULL,
            user_id INTEGER NOT NULL,
            expires_on INTEGER NOT NULL) WITHOUT ROWID"""

@dataclass
class PasswordReset(TableModel):
    token_id: str
    user_id: int
    expires_on: int

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS password_resets(
            token_id TEXT PRIMARY KEY NOT NULL,
            user_id INTEGER NOT NULL,
            expires_on INTEGER NOT NULL) WITHOUT ROWID"""

auth_tables: list[type[TableModel]] = [UserAuth, EmailVerification, PasswordReset]
