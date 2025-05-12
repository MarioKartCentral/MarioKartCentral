from dataclasses import dataclass
from common.data.db.common import IndexModel

# Indexes for UserIPTimeRange table
@dataclass
class UserIPTimeRangesGranularityDateLatest(IndexModel):
    @staticmethod
    def get_create_index_command() -> str:
        return """CREATE INDEX IF NOT EXISTS idx_user_ip_time_ranges_granularity
            ON user_ip_time_ranges(granularity, date_latest)"""

@dataclass
class UserIPTimeRangesUserIPId(IndexModel):
    @staticmethod
    def get_create_index_command() -> str:
        return """CREATE INDEX IF NOT EXISTS idx_user_ip_time_ranges_user_ip_id
            ON user_ip_time_ranges(user_ip_id)"""

# Indexes for UserLogin table
@dataclass
class UserLoginSessionID(IndexModel):
    @staticmethod
    def get_create_index_command() -> str:
        return """CREATE INDEX IF NOT EXISTS idx_user_logins_session_id
            ON user_logins(session_id)"""
    
@dataclass
class UserLoginFingerprintId(IndexModel):
    @staticmethod
    def get_create_index_command() -> str:
        return """CREATE INDEX IF NOT EXISTS idx_user_logins_fingerprint_id
            ON user_logins(fingerprint, id)"""

# Indexes for IPAddress table
@dataclass
class IPAddressIsCheckedIsVPNCheckedAt(IndexModel):
    @staticmethod
    def get_create_index_command() -> str:
        return """CREATE INDEX IF NOT EXISTS idx_ip_addresses_is_checked_is_vpn_checked_at
            ON ip_addresses(is_checked, is_vpn, checked_at)"""

@dataclass
class IPAddressIsCheckedCheckedAt(IndexModel):
    @staticmethod
    def get_create_index_command() -> str:
        return """CREATE INDEX IF NOT EXISTS idx_ip_addresses_is_checked_checked_at
            ON ip_addresses(is_checked, checked_at)"""

# Indexes for UserIP table
@dataclass
class UserIPIPAddressID(IndexModel):
    @staticmethod
    def get_create_index_command() -> str:
        return """CREATE INDEX IF NOT EXISTS idx_user_ips_ip_address_id
            ON user_ips(ip_address_id)"""

all_indices: list[type[IndexModel]] = [
    UserIPTimeRangesGranularityDateLatest,
    UserIPTimeRangesUserIPId,
    UserLoginSessionID,
    IPAddressIsCheckedIsVPNCheckedAt,
    IPAddressIsCheckedCheckedAt,
    UserIPIPAddressID
]
