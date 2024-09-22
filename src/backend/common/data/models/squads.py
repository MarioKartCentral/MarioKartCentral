from dataclasses import dataclass
from common.data.models.tournament_registrations import TournamentPlayerDetails


@dataclass
class Squad:
    id: int
    name: str | None
    tag: str | None
    color: int
    is_registered: bool

@dataclass
class CreateSquadRequestData:
    squad_color: int
    squad_name: str | None
    squad_tag: str | None
    mii_name: str | None
    can_host: bool
    selected_fc_id: int | None
    is_bagger_clause: bool

@dataclass
class ForceCreateSquadRequestData(CreateSquadRequestData):
    player_id: int
    roster_ids: list[int]
    representative_ids: list[int]
    bagger_ids: list[int]

@dataclass
class EditMySquadRequestData:
    squad_id: int
    squad_name: str
    squad_tag: str
    squad_color: int

@dataclass
class EditSquadRequestData(EditMySquadRequestData):
    is_registered: bool

@dataclass
class InvitePlayerRequestData:
    squad_id: int
    player_id: int
    is_representative: bool = False
    is_bagger_clause: bool = False

@dataclass
class KickSquadPlayerRequestData:
    squad_id: int
    player_id: int

@dataclass
class AcceptInviteRequestData():
    squad_id: int
    mii_name: str | None
    can_host: bool
    selected_fc_id: int | None

@dataclass
class DeclineInviteRequestData():
    squad_id: int

@dataclass
class UnregisterPlayerRequestData():
    squad_id: int | None

@dataclass
class StaffUnregisterPlayerRequestData():
    squad_id: int | None
    player_id: int

@dataclass
class SquadPlayerDetails(TournamentPlayerDetails):
    is_squad_captain: bool
    is_representative: bool
    is_invite: bool
    is_bagger_clause: bool

@dataclass
class TournamentSquadDetails():
    id: int
    name: str | None
    tag: str | None
    color: int
    timestamp: int
    is_registered: int
    players: list[SquadPlayerDetails]

@dataclass
class MyTournamentRegistrationDetails():
    player_id: int
    tournament_id: int
    squads: list[TournamentSquadDetails]
    player: TournamentPlayerDetails | None

@dataclass
class MakeCaptainRequestData():
    squad_id: int
    player_id: int

@dataclass
class UnregisterSquadRequestData():
    squad_id: int

@dataclass
class TeamTournamentPlayer():
    player_id: int
    is_captain: bool
    is_representative: bool
    is_bagger_clause: bool

@dataclass
class RegisterTeamRequestData():
    squad_color: int
    squad_name: str
    squad_tag: str
    roster_ids: list[int]
    players: list[TeamTournamentPlayer]