from common.emails import EmailService
from common.ip_api import IPService
from common.discord import DiscordService
from common.data.models import IPCheckResponse, IPInfoBasic, DiscordUser, DiscordAuthCallbackData, DiscordAccessTokenResponse


class MockEmailService(EmailService):
    async def send_email(self, to_email: str, subject: str, content: str):
        return


class MockIPService(IPService):
    async def check_ips(self, ips_to_check: list[IPInfoBasic]) -> list[IPCheckResponse]:
        return list(map(lambda x: IPCheckResponse("success"), ips_to_check))


class MockDiscordService(DiscordService):
    @property
    def user(self) -> DiscordUser:
        return DiscordUser("1", "username", "0000", "User", None)

    @property
    def access_token(self) -> DiscordAccessTokenResponse:
        return DiscordAccessTokenResponse("access_token", "Bearer", 600, "refresh_token", "identify")

    async def handle_auth_callback(self, data: DiscordAuthCallbackData) -> tuple[DiscordAccessTokenResponse, DiscordUser]:
        return self.access_token, self.user

    async def get_user(self, access_token: str) -> DiscordUser:
        return self.user

    async def get_avatar(self, discord_id: str, avatar: str) -> bytes:
        return b''

    async def refresh_token(self, refresh_token: str) -> DiscordAccessTokenResponse:
        return self.access_token

    async def revoke_token(self, access_token: str) -> None:
        pass
