from dataclasses import dataclass
from typing import Literal


@dataclass
class UserSettings:
    user_id: int
    avatar: str | None = None
    discord_tag: str | None = None
    about_me: str | None = None
    language: str = 'en-us'
    color_scheme: str = 'light'
    timezone: str = 'UTC'

@dataclass
class EditUserSettingsRequestData:
    avatar: str | None = None
    discord_tag: str | None = None
    about_me: str | None = None
    language: Literal['de', 'en-gb', 'en-us', 'es', 'fr', 'ja'] | None = None
    color_scheme: Literal['light', 'dark'] | None = None
    timezone: str | None = None