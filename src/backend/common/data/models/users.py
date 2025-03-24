from dataclasses import dataclass

from common.data.models.players import PlayerDetailed, Player
from common.data.models.teams import TeamInvite
from common.data.models.tournaments import TournamentInvite
from common.data.models.roles import UserRole, TeamRole, SeriesRole, TournamentRole

@dataclass
class User:
    id: int
    player_id: int | None

@dataclass
class UserAccountInfo(User):
    email_confirmed: bool
    force_password_reset: bool

@dataclass
class ModNotifications:
    pending_teams: int = 0
    pending_team_edits: int = 0
    pending_transfers: int = 0
    pending_player_name_changes: int = 0
    pending_player_claims: int = 0

@dataclass
class UserPlayer(UserAccountInfo):
    player: PlayerDetailed | None
    user_roles: list[UserRole]
    team_roles: list[TeamRole]
    series_roles: list[SeriesRole]
    tournament_roles: list[TournamentRole]
    mod_notifications: ModNotifications | None

@dataclass
class UserLoginData(UserAccountInfo):
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

@dataclass
class UserFilter:
    name_or_email: str | None = None
    page: int | None = None

@dataclass
class EditUserRequestData:
    user_id: int
    email: str
    password: str | None

@dataclass
class UserInfo:
    id: int
    email: str
    join_date: int
    player: Player | None

@dataclass
class UserList:
    users: list[UserInfo]
    user_count: int
    page_count: int