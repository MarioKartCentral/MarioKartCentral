from dataclasses import dataclass
from common.data.db.common import TableModel

@dataclass
class UserLogin(TableModel):
    id: int
    user_id: int
    ip_address_id: int
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
            ip_address_id INTEGER NOT NULL REFERENCES ip_addresses(id),
            session_id TEXT NOT NULL,
            persistent_session_id TEXT NOT NULL,
            fingerprint TEXT NOT NULL,
            had_persistent_session BOOLEAN NOT NULL,
            date INTEGER NOT NULL,
            logout_date INTEGER
        )"""

@dataclass
class IPAddress(TableModel):
    id: int
    ip_address: str
    is_mobile: bool
    is_vpn: bool
    country: str
    is_checked: bool
    checked_at: int | None

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS ip_addresses(
            id INTEGER PRIMARY KEY,
            ip_address TEXT NOT NULL UNIQUE,
            is_mobile BOOLEAN NOT NULL,
            is_vpn BOOLEAN NOT NULL,
            country TEXT,
            region TEXT,
            city TEXT,
            asn TEXT,
            is_checked BOOLEAN NOT NULL,
            checked_at INTEGER
        )"""

@dataclass
class UserIP(TableModel):
    id: int
    user_id: int
    ip_address_id: int

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS user_ips(
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            ip_address_id INTEGER NOT NULL REFERENCES ip_addresses(id),
            UNIQUE(user_id, ip_address_id)
        )"""

@dataclass
class UserIPTimeRange(TableModel):
    id: int
    user_ip_id: int
    date_earliest: int
    date_latest: int
    times: int
    granularity: int = 0  # 0=none, 1=1min, 2=10min, 3=30min, 4=1hr, 5=1day

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS user_ip_time_ranges(
            id INTEGER PRIMARY KEY,
            user_ip_id INTEGER NOT NULL REFERENCES user_ips(id),
            date_earliest INTEGER NOT NULL,
            date_latest INTEGER NOT NULL,
            times INTEGER NOT NULL,
            granularity INTEGER NOT NULL DEFAULT 0
        )"""

all_tables: list[type[TableModel]] = [UserLogin, IPAddress, UserIP, UserIPTimeRange]
