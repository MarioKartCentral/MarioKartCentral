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
    registration_id: int | None = None
    is_squad_captain: bool = False
    is_invite: bool = False
    is_checked_in: bool = False
    is_representative: bool = False
    is_bagger_clause: bool = False
    is_approved: bool = False

@dataclass
class EditMyRegistrationRequestData():
    mii_name: str | None
    can_host: bool
    selected_fc_id: int | None
    registration_id: int

@dataclass
class EditPlayerRegistrationRequestData(EditMyRegistrationRequestData):
    player_id: int
    is_squad_captain: bool | None
    is_invite: bool
    is_checked_in: bool | None
    is_representative: bool | None
    is_bagger_clause: bool | None
    is_approved: bool | None

@dataclass
class TournamentPlayerDetailsShort():
    player_id: int
    player_name: str
    registration_id: int

@dataclass
class TournamentPlayerDetails():
    id: int
    player_id: int
    registration_id: int
    timestamp: int
    is_checked_in: bool
    is_approved: bool
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
    is_approved: bool | None = None

@dataclass
class TournamentCheckinRequestData():
    registration_id: int
