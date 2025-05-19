from dataclasses import dataclass
from common.data.db.common import IndexModel


@dataclass
class EmailVerificationExpiresOn(IndexModel):
    @staticmethod
    def get_create_index_command() -> str:
        return """CREATE INDEX IF NOT EXISTS idx_email_verifications_expires_on
            ON email_verifications(expires_on)"""


@dataclass
class PasswordResetExpiresOn(IndexModel):
    @staticmethod
    def get_create_index_command() -> str:
        return """CREATE INDEX IF NOT EXISTS idx_password_resets_expires_on
            ON password_resets(expires_on)"""


all_indices: list[type[IndexModel]] = [
    EmailVerificationExpiresOn,
    PasswordResetExpiresOn
]
