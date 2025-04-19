from dataclasses import dataclass
from common.data.models.tournament_registrations import TournamentPlayerDetails
from common.data.models.teams import RosterBasic

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
    is_checked_in: bool = False
    is_approved: bool = False

@dataclass
class EditMySquadRequestData:
    registration_id: int
    squad_name: str | None
    squad_tag: str | None
    squad_color: int | None

@dataclass
class EditSquadRequestData(EditMySquadRequestData):
    is_registered: bool | None = None
    is_approved: bool | None = None

@dataclass
class InvitePlayerRequestData:
    registration_id: int
    player_id: int
    is_representative: bool = False
    is_bagger_clause: bool = False

@dataclass
class KickSquadPlayerRequestData:
    registration_id: int
    player_id: int

@dataclass
class AcceptInviteRequestData():
    registration_id: int
    mii_name: str | None
    can_host: bool
    selected_fc_id: int | None

@dataclass
class DeclineInviteRequestData():
    registration_id: int

@dataclass
class UnregisterPlayerRequestData():
    registration_id: int

@dataclass
class StaffUnregisterPlayerRequestData(UnregisterPlayerRequestData):
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
    is_registered: bool
    is_approved: bool
    players: list[SquadPlayerDetails]
    rosters: list[RosterBasic]

@dataclass
class MyTournamentRegistration():
    squad: TournamentSquadDetails
    player: TournamentPlayerDetails

@dataclass
class MyTournamentRegistrationDetails():
    player_id: int
    tournament_id: int
    registrations: list[MyTournamentRegistration]

@dataclass
class MakeCaptainRequestData():
    registration_id: int
    player_id: int

@dataclass
class UnregisterSquadRequestData():
    registration_id: int

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

@dataclass
class AddRemoveRosterRequestData:
    registration_id: int
    roster_id: int