from dataclasses import dataclass

@dataclass
class LinkDiscordRequestData:
    page_url: str | None = None

@dataclass
class DiscordAuthCallbackData:
    code: str
    state: str | None = None

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