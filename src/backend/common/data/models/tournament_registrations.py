from dataclasses import dataclass

@dataclass
class RegisterTeamRequestData:
    squad_color: str
    squad_name: str
    squad_tag: str
    captain_player: int
    roster_ids: list[int]
    representative_ids: list[int]

@dataclass
class RegisterPlayerRequestData:
    mii_name: str | None
    can_host: bool
    selected_fc_id: int | None

@dataclass
class ForceRegisterPlayerRequestData(RegisterPlayerRequestData):
    squad_id: int | None
    player_id: int
    is_squad_captain: bool
    is_invite: bool
    is_checked_in: bool
    is_representative: bool

@dataclass
class EditPlayerRegistrationRequestData():
    player_id: int
    squad_id: int | None
    is_squad_captain: bool
    is_invite: bool
    is_checked_in: bool
    can_host: bool
    mii_name: str | None
    selected_fc_id: int | None
    is_representative: bool

@dataclass
class TournamentPlayerDetails():
    player_id: int
    squad_id: int | None
    timestamp: int
    is_checked_in: bool
    mii_name: str | None
    can_host: bool
    name: str
    country_code: str | None
    discord_id: str | None
    friend_codes: list[str]

@dataclass
class TournamentRegistrationFilter():
    registered_only: bool = True
    eligible_only: bool = False
    hosts_only: bool = False