from dataclasses import dataclass
from common.data.models.friend_codes import FriendCode
from common.data.models.discord_integration import Discord

@dataclass
class RegisterPlayerRequestData:
    mii_name: str | None
    can_host: bool
    selected_fc_id: int | None

@dataclass
class ForceRegisterPlayerRequestData(RegisterPlayerRequestData):
    player_id: int
    squad_id: int | None = None
    is_squad_captain: bool = False
    is_invite: bool = False
    is_checked_in: bool = False
    is_representative: bool = False
    is_bagger_clause: bool = False

@dataclass
class EditMyRegistrationRequestData():
    mii_name: str | None
    can_host: bool
    selected_fc_id: int | None
    squad_id: int | None

@dataclass
class EditPlayerRegistrationRequestData(EditMyRegistrationRequestData):
    player_id: int
    is_squad_captain: bool | None
    is_invite: bool
    is_checked_in: bool | None
    is_representative: bool | None
    is_bagger_clause: bool | None

@dataclass
class TournamentPlayerDetails():
    id: int
    player_id: int
    squad_id: int | None
    timestamp: int
    is_checked_in: bool
    mii_name: str | None
    can_host: bool
    name: str
    country_code: str | None
    discord: Discord | None
    selected_fc_id: int | None
    friend_codes: list[FriendCode]

@dataclass
class TournamentRegistrationFilter():
    registered_only: bool = True
    eligible_only: bool = False
    hosts_only: bool = False