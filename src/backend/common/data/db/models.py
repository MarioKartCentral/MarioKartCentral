from abc import ABC, abstractmethod
from dataclasses import dataclass

class TableModel(ABC):
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
    discord_id: str

    @staticmethod
    def get_create_table_command():
        return """CREATE TABLE IF NOT EXISTS players(
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            country_code TEXT NOT NULL,
            is_hidden INTEGER NOT NULL,
            is_shadow INTEGER NOT NULL,
            is_banned INTEGER NOT NULL,
            discord_id TEXT NOT NULL)"""

@dataclass
class FriendCode(TableModel):
    player_id: int
    fc: str
    is_verified: int
    game: str

    @staticmethod
    def get_create_table_command():
        return """CREATE TABLE IF NOT EXISTS friend_codes(
            player_id INTEGER NOT NULL,
            fc TEXT NOT NULL,
            is_verified INTEGER NOT NULL,
            game TEXT NOT NULL,
            PRIMARY KEY(player_id, fc, game)) WITHOUT ROWID"""

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

    @staticmethod
    def get_create_table_command():
        return """CREATE TABLE IF NOT EXISTS tournaments(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            game TEXT NOT NULL,
            mode TEXT NOT NULL,
            series_id INTEGER REFERENCES tournament_series(id),
            is_squad INTEGER NOT NULL,
            registrations_open INTEGER NOT NULL,
            date_start INTEGER NOT NULL,
            date_end INTEGER NOT NULL,
            description TEXT NOT NULL,
            use_series_description INTEGER NOT NULL,
            series_stats_include INTEGER NOT NULL,
            logo TEXT,
            url TEXT UNIQUE,
            registration_deadline INTEGER,
            registration_cap INTEGER,
            teams_allowed INTEGER NOT NULL,
            teams_only INTEGER NOT NULL,
            team_members_only INTEGER NOT NULL,
            min_squad_size INTEGER,
            max_squad_size INTEGER,
            squad_tag_required INTEGER NOT NULL,
            squad_name_required INTEGER NOT NULL,
            mii_name_required INTEGER NOT NULL,
            host_status_required INTEGER NOT NULL,
            checkins_open INTEGER NOT NULL,
            min_players_checkin INTEGER NOT NULL,
            verified_fc_required INTEGER NOT NULL,
            is_viewable INTEGER NOT NULL,
            is_public INTEGER NOT NULL,
            show_on_profiles INTEGER NOT NULL)"""

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
    can_hots: bool
    is_invite: bool

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
            is_invite INTEGER NOT NULL)"""