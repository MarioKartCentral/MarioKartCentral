from dataclasses import dataclass
from common.data.db.common import IndexModel

@dataclass
class AltFlagsType(IndexModel):
    @staticmethod
    def get_create_index_command() -> str:
        return """CREATE INDEX IF NOT EXISTS idx_alt_flags_type
            ON alt_flags(type)"""

@dataclass
class AltFlagsDate(IndexModel):
    @staticmethod
    def get_create_index_command() -> str:
        return """CREATE INDEX IF NOT EXISTS idx_alt_flags_date
            ON alt_flags(date DESC)"""

@dataclass
class UserAltFlagsFlagId(IndexModel):
    @staticmethod
    def get_create_index_command() -> str:
        return """CREATE INDEX IF NOT EXISTS idx_user_alt_flags_flag_id
            ON user_alt_flags(flag_id)"""

all_indices: list[type[IndexModel]] = [
    AltFlagsType,
    AltFlagsDate,
    UserAltFlagsFlagId
]
