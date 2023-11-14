from dataclasses import dataclass

from common.data.models.players import PlayerDetailed
from common.data.models.teams import TeamInvite
from common.data.models.tournaments import TournamentInvite

@dataclass
class User:
    id: int
    player_id: int | None

@dataclass
class ModNotifications:
    pending_teams: int = 0
    pending_team_edits: int = 0
    pending_transfers: int = 0

@dataclass
class TeamPermissions:
    team_id: int
    permissions: list[str]

@dataclass
class SeriesPermissions:
    series_id: int
    permissions: list[str]

@dataclass
class UserPlayer:
    id: int
    player_id: int | None
    player: PlayerDetailed | None
    permissions: list[str]
    team_permissions: list[TeamPermissions]
    series_permissions: list[str]
    mod_notifications: ModNotifications | None

@dataclass
class UserLoginData(User):
    email: str
    password_hash: str

@dataclass
class PermissionsCheck:
    permissions: str | None = None
    check_team_perms: bool = False
    check_series_perms: bool = False

@dataclass
class PlayerInvites:
    player_id: int
    team_invites: list[TeamInvite]
    tournament_invites: list[TournamentInvite]