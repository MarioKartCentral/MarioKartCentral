from dataclasses import dataclass
from common.data.models.players import Player

@dataclass
class Permission:
    name: str
    is_denied: bool

@dataclass
class Role:
    id: int
    name: str
    position: int

@dataclass
class RoleInfo(Role):
    permissions: list[Permission]
    players: list[Player]

@dataclass
class TeamRoleInfo(RoleInfo):
    team_id: int

@dataclass
class SeriesRoleInfo(RoleInfo):
    series_id: int

@dataclass
class TournamentRoleInfo(RoleInfo):
    tournament_id: int

@dataclass
class UserRole(Role):
    expires_on: int | None
    permissions: list[Permission]

@dataclass
class TeamRole(UserRole):
    team_id: int

@dataclass
class SeriesRole(UserRole):
    series_id: int

@dataclass
class TournamentRole(UserRole):
    tournament_id: int

@dataclass
class RemoveRoleRequestData:
    player_id: int
    role_name: str

@dataclass
class GrantRoleRequestData(RemoveRoleRequestData):
    expires_on: int | None = None

@dataclass
class RolePlayer(Player):
    expires_on: int | None = None