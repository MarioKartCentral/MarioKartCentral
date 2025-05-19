from dataclasses import dataclass
from common.data.db.common import IndexModel


@dataclass
class DiscordTokensExpiresOn(IndexModel):
    @staticmethod
    def get_create_index_command() -> str:
        return """CREATE INDEX IF NOT EXISTS idx_discord_tokens_token_expires_on
            ON discord_tokens(token_expires_on)"""


all_indices: list[type[IndexModel]] = [
    DiscordTokensExpiresOn
]
