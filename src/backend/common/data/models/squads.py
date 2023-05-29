from dataclasses import dataclass
from typing import List

from common.data.models.tournament_registrations import TournamentPlayerDetails


@dataclass
class Squad:
    id: int
    name: str
    tag: str
    color: str
    is_registered: bool

@dataclass
class CreateSquadRequestData:
    squad_color: str
    squad_name: str | None
    squad_tag: str | None
    mii_name: str | None
    can_host: bool
    selected_fc_id: int | None

@dataclass
class ForceCreateSquadRequestData(CreateSquadRequestData):
    player_id: int
    roster_ids: List[int]
    representative_ids: List[int]

@dataclass
class EditSquadRequestData:
    squad_id: int
    squad_name: str
    squad_tag: str
    squad_color: str
    is_registered: bool

# actually used for both inviting and kicking players from squads
@dataclass
class InvitePlayerRequestData:
    squad_id: int
    player_id: int
    is_representative: bool = False


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
    is_squad_captain: int
    is_invite: bool

@dataclass
class TournamentSquadDetails():
    id: int
    name: str | None
    tag: str | None
    color: int
    timestamp: int
    is_registered: int
    players: List[TournamentPlayerDetails]