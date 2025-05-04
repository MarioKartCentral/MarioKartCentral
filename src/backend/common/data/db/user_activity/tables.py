from dataclasses import dataclass
from typing import List, Type
from common.data.db.common import TableModel

@dataclass
class UserLogin(TableModel):
    id: int
    user_id: int
    ip: str
    session_id: str
    persistent_session_id: str
    fingerprint: str
    had_persistent_session: bool
    date: int
    logout_date: int | None

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS user_logins(
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            ip TEXT NOT NULL,
            session_id TEXT NOT NULL,
            persistent_session_id TEXT NOT NULL,
            fingerprint TEXT NOT NULL,
            had_persistent_session BOOLEAN NOT NULL,
            date INTEGER NOT NULL,
            logout_date INTEGER
        )"""
    
@dataclass
class UserIP(TableModel):
    user_id: int
    ip_address: str
    date_earliest: int
    date_latest: int
    times: int
    is_mobile: bool
    is_vpn: bool
    is_checked: bool

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS user_ips(
            user_id INTEGER NOT NULL REFERENCES users(id),
            ip_address TEXT NOT NULL,
            date_earliest INTEGER NOT NULL,
            date_latest INTEGER NOT NULL,
            times INTEGER NOT NULL,
            is_mobile BOOLEAN NOT NULL,
            is_vpn BOOLEAN NOT NULL,
            is_checked BOOLEAN NOT NULL,
            PRIMARY KEY(user_id, ip_address)) WITHOUT ROWID"""

all_tables: List[Type[TableModel]] = [UserLogin, UserIP]
