from dataclasses import dataclass
from typing import Literal


@dataclass
class Notification:
    id: int
    type: int
    content_id: int
    content_args: dict[str, str]
    link: str
    created_date: int
    is_read: bool

@dataclass
class NotificationFilter:
    is_read: Literal['0', '1'] | None = None
    type: str | None = None # separate multiple types with commas
    before: str | None = None
    after: str | None = None

@dataclass
class MarkAsReadRequestData:
    is_read: bool

@dataclass
class NotificationDataTournamentSquad:
    squad_name: str | None
    tournament_name: str
    captain_user_id: int

@dataclass
class NotificationDataUser:
    user_id: int
    player_id: int

@dataclass
class NotificationDataTeam:
    team_id: int
    team_name: str

@dataclass
class NotificationDataTeamRoster:
    team_id: int
    team_name: str
    roster_name: str | None

@dataclass
class NotificationDataTeamTransfer:
    player_name: str
    player_id: int
    team_id: int
    team_name: str
    roster_name: str
