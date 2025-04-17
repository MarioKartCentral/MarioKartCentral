from dataclasses import dataclass

@dataclass
class DiscordAuthCallbackData:
    code: str | None = None
    state: str | None = None
    error: str | None = None

@dataclass
class DiscordAccessTokenResponse:
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    scope: str

@dataclass
class DiscordUser:
    id: str
    username: str
    discriminator: str
    global_name: str | None
    avatar: str | None

@dataclass
class Discord:
    discord_id: str
    username: str
    discriminator: str
    global_name: str | None
    avatar: str | None

@dataclass
class MyDiscordData(Discord):
    user_id: int