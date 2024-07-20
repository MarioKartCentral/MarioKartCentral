from dataclasses import dataclass

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

