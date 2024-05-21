from abc import ABC, abstractmethod
from dataclasses import dataclass

class TableModel(ABC):
    @staticmethod
    @abstractmethod
    def get_create_table_command() -> str:
        pass

@dataclass
class Player(TableModel):
    id: int
    name: str
    country_code: str
    is_hidden: bool
    is_shadow: bool
    is_banned: bool
    discord_id: str | None

    @staticmethod
    def get_create_table_command():
        return """CREATE TABLE IF NOT EXISTS players(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            country_code TEXT NOT NULL,
            is_hidden BOOLEAN NOT NULL,
            is_shadow BOOLEAN NOT NULL,
            is_banned BOOLEAN NOT NULL,
            discord_id TEXT)"""

@dataclass
class FriendCode(TableModel):
    id: int
    player_id: int
    game: str
    fc: str
    is_verified: bool
    is_primary: bool
    is_active: bool
    description: str

    @staticmethod
    def get_create_table_command():
        return """CREATE TABLE IF NOT EXISTS friend_codes(
            id INTEGER PRIMARY KEY,
            player_id INTEGER NOT NULL,
            game TEXT NOT NULL,
            fc TEXT NOT NULL,
            is_verified BOOLEAN NOT NULL,
            is_primary BOOLEAN NOT NULL,
            is_active BOOLEAN NOT NULL,
            description TEXT
            )"""

@dataclass
class User(TableModel):
    id: int
    player_id: int
    email: str
    password_hash: str

    @staticmethod
    def get_create_table_command():
        return """CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            player_id INTEGER REFERENCES players(id),
            email TEXT UNIQUE,
            password_hash TEXT)"""

@dataclass
class Session(TableModel):
    session_id: str
    user_id: int
    expires_on: int

    @staticmethod
    def get_create_table_command():
        return """CREATE TABLE IF NOT EXISTS sessions(
            session_id TEXT PRIMARY KEY NOT NULL,
            user_id INTEGER NOT NULL REFERENCES users(id),
            expires_on INTEGER NOT NULL) WITHOUT ROWID"""

@dataclass
class Role(TableModel):
    id: int
    name: str

    @staticmethod
    def get_create_table_command():
        return """CREATE TABLE IF NOT EXISTS roles(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL)"""

@dataclass
class Permission(TableModel):
    id: int
    name: str

    @staticmethod
    def get_create_table_command():
        return """CREATE TABLE IF NOT EXISTS permissions(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL)"""

@dataclass
class UserRole(TableModel):
    user_id: int
    role_id: int

    @staticmethod
    def get_create_table_command():
        return """CREATE TABLE IF NOT EXISTS user_roles(
            user_id INTEGER NOT NULL REFERENCES users(id),
            role_id INTEGER NOT NULL REFERENCES roles(id),
            PRIMARY KEY (user_id, role_id)) WITHOUT ROWID"""

@dataclass
class RolePermission(TableModel):
    role_id: int
    permission_id: int

    @staticmethod
    def get_create_table_command():
        return """CREATE TABLE IF NOT EXISTS role_permissions(
            role_id INTEGER NOT NULL REFERENCES roles(id),
            permission_id INTEGER NOT NULL REFERENCES permissions(id),
            PRIMARY KEY (role_id, permission_id)) WITHOUT ROWID"""

@dataclass
class TournamentSeries(TableModel):
    id: int
    name: str
    url: str
    game: str
    mode: str
    is_historical: bool
    is_public: bool
    description: str
    ruleset: str
    logo: str | None

    @staticmethod
    def get_create_table_command():
        return """CREATE TABLE IF NOT EXISTS tournament_series(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            url TEXT UNIQUE,
            display_order INTEGER NOT NULL,
            game TEXT NOT NULL,
            mode TEXT NOT NULL,
            is_historical INTEGER NOT NULL,
            is_public INTEGER NOT NULL,
            description TEXT NOT NULL,
            ruleset TEXT NOT NULL,
            logo TEXT)"""

@dataclass
class Tournament(TableModel):
    id: int
    name: str
    game: str
    mode: str
    series_id: int | None
    is_squad: bool
    registrations_open: bool
    date_start: int
    date_end: int
    description: str
    use_series_description: bool
    series_stats_include: bool
    logo: str | None
    url: str
    registration_deadline: int | None
    registration_cap: int | None
    teams_allowed: bool
    teams_only: bool
    team_members_only: bool
    min_squad_size: int | None
    max_squad_size: int | None
    squad_tag_required: bool
    squad_name_required: bool
    mii_name_required: bool
    host_status_required: bool
    checkins_open: bool
    min_players_checkin: int | None
    verification_required: bool
    verified_fc_required: bool
    is_viewable: bool
    is_public: bool
    is_deleted: bool
    show_on_profiles: bool
    require_single_fc: bool
    min_representatives: int | None

    @staticmethod
    def get_create_table_command():
        return """CREATE TABLE IF NOT EXISTS tournaments(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            game TEXT NOT NULL,
            mode TEXT NOT NULL,
            series_id INTEGER REFERENCES tournament_series(id),
            is_squad BOOLEAN NOT NULL,
            registrations_open BOOLEAN NOT NULL,
            date_start INTEGER NOT NULL,
            date_end INTEGER NOT NULL,
            description TEXT NOT NULL,
            use_series_description BOOLEAN NOT NULL,
            series_stats_include BOOLEAN NOT NULL,
            logo TEXT,
            use_series_logo BOOLEAN NOT NULL,
            url TEXT UNIQUE,
            registration_deadline INTEGER,
            registration_cap INTEGER,
            teams_allowed BOOLEAN NOT NULL,
            teams_only BOOLEAN NOT NULL,
            team_members_only BOOLEAN NOT NULL,
            min_squad_size INTEGER,
            max_squad_size INTEGER,
            squad_tag_required BOOLEAN NOT NULL,
            squad_name_required BOOLEAN NOT NULL,
            mii_name_required BOOLEAN NOT NULL,
            host_status_required BOOLEAN NOT NULL,
            checkins_open BOOLEAN NOT NULL,
            min_players_checkin INTEGER,
            verification_required BOOLEAN NOT NULL,
            verified_fc_required BOOLEAN NOT NULL,
            is_viewable BOOLEAN NOT NULL,
            is_public BOOLEAN NOT NULL,
            is_deleted BOOLEAN NOT NULL,
            show_on_profiles BOOLEAN NOT NULL,
            require_single_fc BOOLEAN NOT NULL,
            min_representatives INTEGER
            )"""

@dataclass
class TournamentTemplate(TableModel):
    id: int
    name: str
    series_id: int | None

    @staticmethod
    def get_create_table_command():
        return """CREATE TABLE IF NOT EXISTS tournament_templates(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            series_id INTEGER REFERENCES tournament_series(id))"""

@dataclass
class TournamentSquad(TableModel):
    id: int
    name: str | None
    tag: str | None
    color: int
    timestamp: int
    tournament_id: int
    is_registered: int

    @staticmethod
    def get_create_table_command():
        return """CREATE TABLE IF NOT EXISTS tournament_squads(
            id INTEGER PRIMARY KEY,
            name TEXT,
            tag TEXT,
            color INTEGER NOT NULL,
            timestamp INTEGER NOT NULL,
            tournament_id INTEGER NOT NULL REFERENCES tournaments(id),
            is_registered INTEGER NOT NULL)"""

@dataclass
class TournamentPlayer(TableModel):
    id: int
    player_id: int
    tournament_id: int
    squad_id: int | None
    is_squad_captain: bool
    timestamp: int
    is_checked_in: bool
    mii_name: str | None
    can_host: bool
    is_invite: bool
    selected_fc_id: int
    is_representative: bool

    @staticmethod
    def get_create_table_command():
        return """CREATE TABLE IF NOT EXISTS tournament_players(
            id INTEGER PRIMARY KEY,
            player_id INTEGER NOT NULL REFERENCES players(id),
            tournament_id INTEGER NOT NULL REFERENCES tournaments(id),
            squad_id INTEGER REFERENCES tournament_squads(id),
            is_squad_captain BOOLEAN,
            timestamp INTEGER NOT NULL,
            is_checked_in BOOLEAN NOT NULL,
            mii_name TEXT,
            can_host BOOLEAN NOT NULL,
            is_invite BOOLEAN NOT NULL,
            selected_fc_id INTEGER,
            is_representative BOOLEAN NOT NULL
            )"""
    
@dataclass
class TournamentSoloPlacements(TableModel):
    id: int
    tournament_id: int
    player_id: int
    placement: int
    placement_description: str
    placement_lower_bound: int | None
    is_disqualified: bool

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS tournament_solo_placements(
            id INTEGER PRIMARY KEY,
            tournament_id INTEGER NOT NULL REFERENCES tournaments(id),
            player_id INTEGER NOT NULL REFERENCES tournament_players(id),
            placement INTEGER,
            placement_description TEXT,
            placement_lower_bound INTEGER,
            is_disqualified BOOLEAN NOT NULL
        )"""
    
@dataclass
class TournamentSquadPlacements(TableModel):
    id: int
    tournament_id: int
    squad_id: int
    placement: int
    placement_description: str
    placement_lower_bound: int | None
    is_disqualified: bool

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS tournament_squad_placements(
            id INTEGER PRIMARY KEY,
            tournament_id INTEGER NOT NULL REFERENCES tournaments(id),
            squad_id INTEGER NOT NULL REFERENCES tournament_squads(id),
            placement INTEGER,
            placement_description TEXT,
            placement_lower_bound INTEGER,
            is_disqualified BOOLEAN NOT NULL
        )"""
    
@dataclass
class Team(TableModel):
    id: int
    name: str
    tag: str
    description: str
    creation_date: int
    language: str
    color: int
    logo: str | None
    approval_status: str
    is_historical: bool

    @staticmethod
    def get_create_table_command():
        return """CREATE TABLE IF NOT EXISTS teams(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            tag TEXT NOT NULL,
            description TEXT NOT NULL,
            creation_date INTEGER NOT NULL,
            language TEXT NOT NULL,
            color INTEGER NOT NULL,
            logo TEXT,
            approval_status TEXT NOT NULL,
            is_historical BOOLEAN NOT NULL
            )
            """

@dataclass
class TeamRoster(TableModel):
    id: int
    team_id: int
    game: str
    mode: str
    name: str | None
    tag: str | None
    creation_date: int
    is_recruiting: bool
    is_active: bool
    approval_status: str

    @staticmethod
    def get_create_table_command():
        return """CREATE TABLE IF NOT EXISTS team_rosters(
            id INTEGER PRIMARY KEY,
            team_id INTEGER NOT NULL REFERENCES teams(id),
            game TEXT NOT NULL,
            mode TEXT NOT NULL,
            name TEXT,
            tag TEXT,
            creation_date INTEGER NOT NULL,
            is_recruiting BOOLEAN NOT NULL,
            is_active BOOLEAN NOT NULL,
            approval_status STRING NOT NULL
            )
            """

@dataclass
class TeamMember(TableModel):
    id: int
    roster_id: int
    player_id: int
    join_date: int
    leave_date: int | None

    @staticmethod
    def get_create_table_command():
        return """CREATE TABLE IF NOT EXISTS team_members(
            id INTEGER PRIMARY KEY,
            roster_id INTEGER NOT NULL REFERENCES team_rosters(id),
            player_id INTEGER NOT NULL REFERENCES players(id),
            join_date INTEGER NOT NULL,
            leave_date INTEGER
            )
            """

@dataclass
class TeamSquadRegistration(TableModel):
    roster_id: int
    squad_id: int
    tournament_id: int

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS team_squad_registrations(
            roster_id INTEGER NOT NULL,
            squad_id INTEGER NOT NULL,
            tournament_id INTEGER NOT NULL,
            PRIMARY KEY (roster_id, squad_id, tournament_id)
            ) WITHOUT ROWID
            """

@dataclass
class TeamRole(TableModel):
    id: int
    name: str

    @staticmethod
    def get_create_table_command():
        return """CREATE TABLE IF NOT EXISTS team_roles(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL)"""
    
@dataclass
class TeamPermission(TableModel):
    id: int
    name: str

    @staticmethod
    def get_create_table_command():
        return """CREATE TABLE IF NOT EXISTS team_permissions(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL)"""
    
@dataclass
class TeamRolePermission(TableModel):
    role_id: int
    permission_id: int

    @staticmethod
    def get_create_table_command():
        return """CREATE TABLE IF NOT EXISTS team_role_permissions(
            role_id INTEGER NOT NULL REFERENCES team_roles(id),
            permission_id INTEGER NOT NULL REFERENCES team_permissions(id),
            PRIMARY KEY (role_id, permission_id)) WITHOUT ROWID"""

@dataclass
class UserTeamRole(TableModel):
    user_id: int
    role_id: int
    team_id: int

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS user_team_roles(
            user_id INTEGER NOT NULL REFERENCES users(id),
            role_id INTEGER NOT NULL REFERENCES team_roles(id),
            team_id INTEGER NOT NULL REFERENCES teams(id),
            PRIMARY KEY (user_id, role_id, team_id)
            ) WITHOUT ROWID
            """

@dataclass
class SeriesRole(TableModel):
    id: int
    name: str

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS series_roles(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL)"""
    
@dataclass
class SeriesPermission(TableModel):
    id: int
    name: str

    @staticmethod
    def get_create_table_command():
        return """CREATE TABLE IF NOT EXISTS series_permissions(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL)"""
    
@dataclass
class SeriesRolePermission(TableModel):
    role_id: int
    permission_id: int

    @staticmethod
    def get_create_table_command():
        return """CREATE TABLE IF NOT EXISTS series_role_permissions(
            role_id INTEGER NOT NULL REFERENCES series_roles(id),
            permission_id INTEGER NOT NULL REFERENCES series_permissions(id),
            PRIMARY KEY (role_id, permission_id)) WITHOUT ROWID"""

@dataclass
class UserSeriesRole(TableModel):
    user_id: int
    role_id: int
    series_id: int

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS user_series_roles (
            user_id INTEGER NOT NULL REFERENCES users(id),
            role_id INTEGER NOT NULL REFERENCES series_roles(id),
            series_id INTEGER NOT NULL REFERENCES tournament_series(id),
            PRIMARY KEY (user_id, role_id, series_id)
            ) WITHOUT ROWID
            """

@dataclass
class RosterInvite(TableModel):
    id: int
    player_id: int
    roster_id: int
    date: int
    roster_leave_id: int
    is_accepted: int
    approval_status: str

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS team_transfers (
            id INTEGER PRIMARY KEY,
            player_id INTEGER NOT NULL REFERENCES players(id),
            roster_id INTEGER REFERENCES team_rosters(id),
            date INTEGER NOT NULL,
            roster_leave_id INTEGER REFERENCES team_rosters(id),
            is_accepted BOOLEAN NOT NULL,
            approval_status TEXT NOT NULL 
            )"""

@dataclass
class TeamEditRequest(TableModel):
    id: int
    team_id: int
    name: str | None
    tag: str | None

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS team_edit_requests (
            id INTEGER PRIMARY KEY,
            team_id INTEGER NOT NULL REFERENCES teams(id),
            name TEXT,
            tag TEXT,
            date INTEGER NOT NULL,
            approval_status TEXT NOT NULL
            )"""
    
@dataclass
class RosterEditRequest(TableModel):
    id: int
    roster_id: int
    name: str | None
    tag: str | None

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS roster_edit_requests (
        id INTEGER PRIMARY KEY,
        roster_id INTEGER NOT NULL REFERENCES team_rosters(id),
        name TEXT,
        tag TEXT,
        date INTEGER NOT NULL,
        approval_status TEXT NOT NULL
        )
        """
    
@dataclass
class UserSettings(TableModel):
    user_id: int
    avatar: str | None
    discord_tag: str | None
    about_me: str | None
    language: str
    color_scheme: str
    timezone: str

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS user_settings(
            user_id INTEGER PRIMARY KEY REFERENCES users(id),
            avatar TEXT,
            about_me TEXT,
            language TEXT DEFAULT 'en-us' NOT NULL,
            color_scheme TEXT DEFAULT 'light' NOT NULL,
            timezone TEXT DEFAULT 'UTC' NOT NULL
            ) WITHOUT ROWID"""
    
@dataclass
class NotificationContent(TableModel):
    id: int
    content: str

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS notification_content(
            id INTEGER PRIMARY KEY,
            content TEXT NOT NULL)"""

@dataclass
class Notifications(TableModel):
    id: int
    user_id: int
    type: int
    content_id: int
    created_date: int
    content_is_shared: int
    is_read: int

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS notifications(
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            type INTEGER DEFAULT 0 NOT NULL,
            content_id INTEGER NOT NULL REFERENCES notification_content(id),
            created_date INTEGER NOT NULL,
            content_is_shared INTEGER NOT NULL,
            is_read INTEGER DEFAULT 0 NOT NULL)"""

@dataclass
class CommandLog(TableModel):
    id: int
    type: str
    data: str
    timestamp: int

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS command_log(
        id INTEGER PRIMARY KEY autoincrement,
        type TEXT NOT NULL,
        data TEXT NOT NULL,
        timestamp INTEGER NOT NULL DEFAULT (cast(strftime('%s','now') as int)))"""

@dataclass
class PlayerBans(TableModel):
    player_id: int
    staff_id: int
    is_indefinite: bool
    expiration_date: int
    reason: str

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS player_bans(
            player_id INTEGER PRIMARY KEY REFERENCES players(id),
            staff_id INTEGER NOT NULL REFERENCES users(id),
            is_indefinite BOOLEAN NOT NULL,
            expiration_date INTEGER NOT NULL,
            reason TEXT NOT NULL
            ) WITHOUT ROWID"""
    
all_tables : list[type[TableModel]] = [
    Player, FriendCode, User, Session, Role, Permission, UserRole, RolePermission, 
    TournamentSeries, Tournament, TournamentTemplate, TournamentSquad, TournamentPlayer,
    TournamentSoloPlacements, TournamentSquadPlacements, Team, TeamRoster, TeamMember, 
    TeamSquadRegistration, TeamRole, TeamPermission, TeamRolePermission, UserTeamRole,
    SeriesRole, SeriesPermission, SeriesRolePermission,
    UserSeriesRole, RosterInvite, TeamEditRequest, RosterEditRequest,
    UserSettings, NotificationContent, Notifications, CommandLog, PlayerBans]
