from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Type

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
            name TEXT UNIQUE NOT NULL,
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
    is_verified: int
    is_primary: int
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
    logo: str | None

    @staticmethod
    def get_create_table_command():
        return """CREATE TABLE IF NOT EXISTS tournament_series(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            url TEXT UNIQUE,
            game TEXT NOT NULL,
            mode TEXT NOT NULL,
            is_historical INTEGER NOT NULL,
            is_public INTEGER NOT NULL,
            description TEXT NOT NULL,
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
    min_players_checkin: int
    verified_fc_required: bool
    is_viewable: bool
    is_public: bool
    show_on_profiles: bool
    require_single_fc: bool

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
            min_players_checkin INTEGER NOT NULL,
            verified_fc_required BOOLEAN NOT NULL,
            is_viewable BOOLEAN NOT NULL,
            is_public BOOLEAN NOT NULL,
            show_on_profiles BOOLEAN NOT NULL,
            require_single_fc BOOLEAN NOT NULL
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

    @staticmethod
    def get_create_table_command():
        return """CREATE TABLE IF NOT EXISTS tournament_players(
            id INTEGER PRIMARY KEY,
            player_id INTEGER NOT NULL REFERENCES players(id),
            tournament_id INTEGER NOT NULL REFERENCES tournaments(id),
            squad_id INTEGER REFERENCES tournament_squads(id),
            is_squad_captain INTEGER,
            timestamp INTEGER NOT NULL,
            is_checked_in INTEGER NOT NULL,
            mii_name TEXT,
            can_host INTEGER NOT NULL,
            is_invite INTEGER NOT NULL,
            selected_fc_id INTEGER
            )"""

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
            discord_tag TEXT,
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

    
all_tables : List[Type[TableModel]] = [
    Player, FriendCode, User, Session, Role, Permission, UserRole, RolePermission, 
    TournamentSeries, Tournament, TournamentTemplate, TournamentSquad, TournamentPlayer,
    UserSettings, NotificationContent, Notifications]