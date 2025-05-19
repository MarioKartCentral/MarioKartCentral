from dataclasses import dataclass
from common.data.db.common import TableModel

@dataclass
class Player(TableModel):
    id: int
    name: str
    country_code: str
    is_hidden: bool
    is_shadow: bool
    is_banned: bool
    join_date: int

    @staticmethod
    def get_create_table_command():
        return """CREATE TABLE IF NOT EXISTS players(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            country_code TEXT NOT NULL,
            is_hidden BOOLEAN NOT NULL,
            is_shadow BOOLEAN NOT NULL,
            is_banned BOOLEAN NOT NULL,
            join_date INTEGER NOT NULL DEFAULT 0
            )"""

@dataclass
class FriendCode(TableModel):
    id: int
    player_id: int
    type: str
    fc: str
    is_verified: bool
    is_primary: bool
    is_active: bool
    description: str
    creation_date: int

    @staticmethod
    def get_create_table_command():
        return """CREATE TABLE IF NOT EXISTS friend_codes(
            id INTEGER PRIMARY KEY,
            player_id INTEGER NOT NULL REFERENCES players(id),
            type TEXT NOT NULL,
            fc TEXT NOT NULL,
            is_verified BOOLEAN NOT NULL,
            is_primary BOOLEAN NOT NULL,
            is_active BOOLEAN NOT NULL,
            description TEXT,
            creation_date INTEGER NOT NULL
            )"""

@dataclass
class User(TableModel):
    id: int
    player_id: int | None
    join_date: int

    @staticmethod
    def get_create_table_command():
        return """CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            player_id INTEGER REFERENCES players(id),
            join_date INTEGER NOT NULL DEFAULT 0
            )"""

@dataclass
class UserDiscord(TableModel):
    user_id: int
    discord_id: str
    username: str
    discriminator: str
    global_name: str | None
    avatar: str | None

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS user_discords(
        user_id INTEGER PRIMARY KEY REFERENCES users(id),
        discord_id TEXT NOT NULL,
        username TEXT NOT NULL,
        discriminator TEXT NOT NULL,
        global_name TEXT,
        avatar TEXT
        )"""

@dataclass
class Role(TableModel):
    id: int
    name: str
    position: int

    @staticmethod
    def get_create_table_command():
        return """CREATE TABLE IF NOT EXISTS roles(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            position INTEGER NOT NULL
            )"""

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
    expires_on: int | None

    @staticmethod
    def get_create_table_command():
        return """CREATE TABLE IF NOT EXISTS user_roles(
            user_id INTEGER NOT NULL REFERENCES users(id),
            role_id INTEGER NOT NULL REFERENCES roles(id),
            expires_on INTEGER,
            PRIMARY KEY (user_id, role_id)) WITHOUT ROWID"""

@dataclass
class RolePermission(TableModel):
    role_id: int
    permission_id: int
    is_denied: bool

    @staticmethod
    def get_create_table_command():
        return """CREATE TABLE IF NOT EXISTS role_permissions(
            role_id INTEGER NOT NULL REFERENCES roles(id),
            permission_id INTEGER NOT NULL REFERENCES permissions(id),
            is_denied BOOLEAN DEFAULT FALSE NOT NULL,
            PRIMARY KEY (role_id, permission_id)) WITHOUT ROWID"""

@dataclass
class TournamentSeries(TableModel):
    id: int
    name: str
    url: str
    display_order: int
    game: str
    mode: str
    is_historical: bool
    is_public: bool
    short_description: str
    logo: str | None
    organizer: str
    location: str | None

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
            short_description TEXT NOT NULL,
            logo TEXT,
            organizer TEXT NOT NULL,
            location TEXT,
            discord_invite TEXT
            )"""

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
    use_series_description: bool
    series_stats_include: bool
    logo: str | None
    use_series_logo: bool
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
    checkins_enabled: bool
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
    bagger_clause_enabled: bool
    use_series_ruleset: bool
    organizer: str
    location: str | None

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
            checkins_enabled BOOLEAN NOT NULL,
            checkins_open BOOLEAN NOT NULL,
            min_players_checkin INTEGER,
            verification_required BOOLEAN NOT NULL,
            verified_fc_required BOOLEAN NOT NULL,
            is_viewable BOOLEAN NOT NULL,
            is_public BOOLEAN NOT NULL,
            is_deleted BOOLEAN NOT NULL,
            show_on_profiles BOOLEAN NOT NULL,
            require_single_fc BOOLEAN NOT NULL,
            min_representatives INTEGER,
            bagger_clause_enabled BOOLEAN NOT NULL,
            use_series_ruleset BOOLEAN DEFAULT 0 NOT NULL,
            organizer TEXT NOT NULL,
            location TEXT
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
class TournamentRegistration(TableModel):
    id: int
    name: str | None
    tag: str | None
    color: int
    timestamp: int
    tournament_id: int
    is_registered: bool
    is_approved: bool

    @staticmethod
    def get_create_table_command():
        return """CREATE TABLE IF NOT EXISTS tournament_registrations(
            id INTEGER PRIMARY KEY,
            name TEXT,
            tag TEXT,
            color INTEGER NOT NULL,
            timestamp INTEGER NOT NULL,
            tournament_id INTEGER NOT NULL REFERENCES tournaments(id),
            is_registered BOOLEAN NOT NULL,
            is_approved BOOLEAN DEFAULT FALSE NOT NULL
            )"""

@dataclass
class TournamentPlayer(TableModel):
    id: int
    player_id: int
    tournament_id: int
    registration_id: int
    is_squad_captain: bool
    timestamp: int
    is_checked_in: bool
    mii_name: str | None
    can_host: bool
    is_invite: bool
    selected_fc_id: int | None
    is_representative: bool
    is_bagger_clause: bool
    is_approved: bool

    @staticmethod
    def get_create_table_command():
        return """CREATE TABLE IF NOT EXISTS tournament_players(
            id INTEGER PRIMARY KEY,
            player_id INTEGER NOT NULL REFERENCES players(id),
            tournament_id INTEGER NOT NULL REFERENCES tournaments(id),
            registration_id INTEGER NOT NULL REFERENCES tournament_registrations(id),
            is_squad_captain BOOLEAN NOT NULL,
            timestamp INTEGER NOT NULL,
            is_checked_in BOOLEAN NOT NULL,
            mii_name TEXT,
            can_host BOOLEAN NOT NULL,
            is_invite BOOLEAN NOT NULL,
            selected_fc_id INTEGER,
            is_representative BOOLEAN NOT NULL,
            is_bagger_clause BOOLEAN NOT NULL,
            is_approved BOOLEAN DEFAULT FALSE NOT NULL
            )"""
    
@dataclass
class TournamentPlacements(TableModel):
    id: int
    tournament_id: int
    registration_id: int
    placement: int
    placement_description: str | None
    placement_lower_bound: int | None
    is_disqualified: bool

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS tournament_placements(
            id INTEGER PRIMARY KEY,
            tournament_id INTEGER NOT NULL REFERENCES tournaments(id),
            registration_id INTEGER NOT NULL REFERENCES tournament_registrations(id),
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
    is_bagger_clause: bool

    @staticmethod
    def get_create_table_command():
        return """CREATE TABLE IF NOT EXISTS team_members(
            id INTEGER PRIMARY KEY,
            roster_id INTEGER NOT NULL REFERENCES team_rosters(id),
            player_id INTEGER NOT NULL REFERENCES players(id),
            join_date INTEGER NOT NULL,
            leave_date INTEGER,
            is_bagger_clause BOOLEAN NOT NULL
            )
            """

@dataclass
class TeamSquadRegistration(TableModel):
    roster_id: int
    registration_id: int
    tournament_id: int

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS team_squad_registrations(
            roster_id INTEGER NOT NULL,
            registration_id INTEGER NOT NULL,
            tournament_id INTEGER NOT NULL,
            PRIMARY KEY (roster_id, registration_id, tournament_id)
            ) WITHOUT ROWID
            """

@dataclass
class TeamRole(TableModel):
    id: int
    name: str
    position: int

    @staticmethod
    def get_create_table_command():
        return """CREATE TABLE IF NOT EXISTS team_roles(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            position INTEGER NOT NULL)"""
    
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
    is_denied: bool

    @staticmethod
    def get_create_table_command():
        return """CREATE TABLE IF NOT EXISTS team_role_permissions(
            role_id INTEGER NOT NULL REFERENCES team_roles(id),
            permission_id INTEGER NOT NULL REFERENCES team_permissions(id),
            is_denied BOOLEAN DEFAULT FALSE NOT NULL,
            PRIMARY KEY (role_id, permission_id)) WITHOUT ROWID"""

@dataclass
class UserTeamRole(TableModel):
    user_id: int
    role_id: int
    team_id: int
    expires_on: int | None

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS user_team_roles(
            user_id INTEGER NOT NULL REFERENCES users(id),
            role_id INTEGER NOT NULL REFERENCES team_roles(id),
            team_id INTEGER NOT NULL REFERENCES teams(id),
            expires_on INTEGER,
            PRIMARY KEY (user_id, role_id, team_id)
            ) WITHOUT ROWID
            """

@dataclass
class SeriesRole(TableModel):
    id: int
    name: str
    position: int

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS series_roles(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            position INTEGER NOT NULL)"""
    
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
    is_denied: bool

    @staticmethod
    def get_create_table_command():
        return """CREATE TABLE IF NOT EXISTS series_role_permissions(
            role_id INTEGER NOT NULL REFERENCES series_roles(id),
            permission_id INTEGER NOT NULL REFERENCES series_permissions(id),
            is_denied BOOLEAN DEFAULT FALSE NOT NULL,
            PRIMARY KEY (role_id, permission_id)) WITHOUT ROWID"""

@dataclass
class UserSeriesRole(TableModel):
    user_id: int
    role_id: int
    series_id: int
    expires_on: int | None

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS user_series_roles (
            user_id INTEGER NOT NULL REFERENCES users(id),
            role_id INTEGER NOT NULL REFERENCES series_roles(id),
            series_id INTEGER NOT NULL REFERENCES tournament_series(id),
            expires_on INTEGER,
            PRIMARY KEY (user_id, role_id, series_id)
            ) WITHOUT ROWID
            """
    
@dataclass
class TournamentRole(TableModel):
    id: int
    name: str
    position: int

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS tournament_roles(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            position INTEGER NOT NULL)"""
    
@dataclass
class TournamentPermission(TableModel):
    id: int
    name: str

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS tournament_permissions(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL)"""
    
@dataclass
class TournamentRolePermission(TableModel):
    role_id: int
    permission_id: int
    is_denied: bool

    @staticmethod
    def get_create_table_command():
        return """CREATE TABLE IF NOT EXISTS tournament_role_permissions(
            role_id INTEGER NOT NULL REFERENCES tournament_roles(id),
            permission_id INTEGER NOT NULL REFERENCES tournament_permissions(id),
            is_denied BOOLEAN DEFAULT FALSE NOT NULL,
            PRIMARY KEY (role_id, permission_id)) WITHOUT ROWID"""
    
@dataclass
class UserTournamentRole(TableModel):
    user_id: int
    role_id: int
    tournament_id: int
    expires_on: int | None

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS user_tournament_roles (
            user_id INTEGER NOT NULL REFERENCES users(id),
            role_id INTEGER NOT NULL REFERENCES tournament_roles(id),
            tournament_id INTEGER NOT NULL REFERENCES tournaments(id),
            expires_on INTEGER,
            PRIMARY KEY (user_id, role_id, tournament_id)
            ) WITHOUT ROWID
            """

@dataclass
class TeamTransfer(TableModel):
    id: int
    player_id: int
    roster_id: int
    date: int
    is_bagger_clause: bool
    roster_leave_id: int
    is_accepted: bool
    approval_status: str

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS team_transfers (
            id INTEGER PRIMARY KEY,
            player_id INTEGER NOT NULL REFERENCES players(id),
            roster_id INTEGER REFERENCES team_rosters(id),
            date INTEGER NOT NULL,
            roster_leave_id INTEGER REFERENCES team_rosters(id),
            is_bagger_clause BOOLEAN NOT NULL,
            is_accepted BOOLEAN NOT NULL,
            approval_status TEXT NOT NULL
            )"""

@dataclass
class TeamEdit(TableModel):
    id: int
    team_id: int
    old_name: str
    new_name: str
    old_tag: str
    new_tag: str
    date: int
    approval_status: str
    handled_by: int | None

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS team_edits (
            id INTEGER PRIMARY KEY,
            team_id INTEGER NOT NULL REFERENCES teams(id),
            old_name TEXT NOT NULL,
            new_name TEXT NOT NULL,
            old_tag TEXT NOT NULL,
            new_tag TEXT NOT NULL,
            date INTEGER NOT NULL,
            approval_status TEXT NOT NULL,
            handled_by INTEGER REFERENCES players(id)
            )"""
    
@dataclass
class RosterEdit(TableModel):
    id: int
    roster_id: int
    old_name: str
    new_name: str
    old_tag: str
    new_tag: str
    date: int
    approval_status: str
    handled_by: int | None

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS roster_edits (
        id INTEGER PRIMARY KEY,
        roster_id INTEGER NOT NULL REFERENCES team_rosters(id),
        old_name TEXT NOT NULL,
        new_name TEXT NOT NULL,
        old_tag TEXT NOT NULL,
        new_tag TEXT NOT NULL,
        date INTEGER NOT NULL,
        approval_status TEXT NOT NULL,
        handled_by INTEGER REFERENCES players(id)
        )
        """

@dataclass
class FriendCodeEdit(TableModel):
    id: int
    fc_id: int
    old_fc: str | None
    new_fc: str | None
    is_active: bool | None
    handled_by: int | None
    date: int

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS friend_code_edits(
        id INTEGER PRIMARY KEY,
        fc_id INTEGER NOT NULL REFERENCES friend_codes(id),
        old_fc TEXT,
        new_fc TEXT,
        is_active BOOLEAN,
        handled_by INTEGER REFERENCES players(id),
        date INTEGER NOT NULL
        )"""
    
@dataclass
class UserSettings(TableModel):
    user_id: int
    avatar: str | None
    about_me: str | None
    language: str
    color_scheme: str
    timezone: str
    hide_discord: bool

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS user_settings(
            user_id INTEGER PRIMARY KEY REFERENCES users(id),
            avatar TEXT,
            about_me TEXT,
            language TEXT DEFAULT 'en-us' NOT NULL,
            color_scheme TEXT DEFAULT 'light' NOT NULL,
            timezone TEXT DEFAULT 'UTC' NOT NULL,
            hide_discord BOOLEAN DEFAULT FALSE
            ) WITHOUT ROWID"""

@dataclass
class Notifications(TableModel):
    id: int
    user_id: int
    type: int
    content_id: int
    content_args: str
    link: str
    created_date: int
    is_read: int

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS notifications(
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            type INTEGER DEFAULT 0 NOT NULL,
            content_id INTEGER NOT NULL,
            content_args TEXT NOT NULL,
            link TEXT,
            created_date INTEGER NOT NULL,
            is_read INTEGER DEFAULT 0 NOT NULL)"""



@dataclass
class PlayerBans(TableModel):
    player_id: int
    banned_by: int
    is_indefinite: bool
    ban_date: int
    expiration_date: int
    reason: str
    comment: str

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS player_bans(
            player_id INTEGER PRIMARY KEY REFERENCES players(id),
            banned_by INTEGER NOT NULL REFERENCES users(id),
            is_indefinite BOOLEAN NOT NULL,
            ban_date INTEGER NOT NULL,
            expiration_date INTEGER NOT NULL,
            reason TEXT NOT NULL,
            comment TEXT NOT NULL
            ) WITHOUT ROWID"""
    
@dataclass
class PlayerBansHistorical(TableModel):
    id: int
    player_id: int
    banned_by: int
    unbanned_by: int | None
    unban_date: int
    is_indefinite: bool
    ban_date: int
    expiration_date: int
    reason: str
    comment: str

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS player_bans_historical(
            id INTEGER PRIMARY KEY,
            player_id INTEGER REFERENCES players(id),
            banned_by INTEGER NOT NULL REFERENCES users(id),
            unbanned_by INTEGER REFERENCES users(id),
            unban_date INTEGER NOT NULL,
            is_indefinite BOOLEAN NOT NULL,
            ban_date INTEGER NOT NULL,
            expiration_date INTEGER NOT NULL,
            reason TEXT NOT NULL,
            comment TEXT NOT NULL)"""
    
@dataclass
class PlayerNameEdit(TableModel):
    id: int
    player_id: int
    old_name: str
    new_name: str
    date: int
    approval_status: str
    handled_by: int | None

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS player_name_edits (
            id INTEGER PRIMARY KEY,
            player_id INTEGER NOT NULL REFERENCES players(id),
            old_name TEXT NOT NULL,
            new_name TEXT NOT NULL,
            date INTEGER NOT NULL,
            approval_status TEXT NOT NULL,
            handled_by INTEGER REFERENCES players(id)
            )"""

@dataclass
class PlayerClaim(TableModel):
    id: int
    player_id: int
    claimed_player_id: int
    date: int
    approval_status: str

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS player_claims(
            id INTEGER PRIMARY KEY,
            player_id INTEGER NOT NULL REFERENCES players(id),
            claimed_player_id INTEGER NOT NULL REFERENCES players(id),
            date INTEGER NOT NULL,
            approval_status TEXT NOT NULL
        )"""

    

    
@dataclass
class FilteredWords(TableModel):
    id: int
    word: str

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS filtered_words(
            id INTEGER PRIMARY KEY,
            word TEXT NOT NULL
        )"""
    
@dataclass
class Post(TableModel):
    id: int
    title: str
    is_public: bool
    is_global: bool
    creation_date: int
    created_by: int | None

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS posts(
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            is_public BOOLEAN NOT NULL,
            is_global BOOLEAN NOT NULL,
            creation_date INTEGER NOT NULL,
            created_by INTEGER REFERENCES players(id)
        )"""
    
@dataclass
class SeriesPost(TableModel):
    series_id: int
    post_id: int

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS series_posts(
            series_id INTEGER NOT NULL REFERENCES tournament_series(id),
            post_id INTEGER NOT NULL REFERENCES posts(id),
            PRIMARY KEY (series_id, post_id)) WITHOUT ROWID"""
    
@dataclass
class TournamentPost(TableModel):
    tournament_id: int
    post_id: int

    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS tournament_posts(
            tournament_id INTEGER NOT NULL REFERENCES tournaments(id),
            post_id INTEGER NOT NULL REFERENCES posts(id),
            PRIMARY KEY (tournament_id, post_id)) WITHOUT ROWID"""


@dataclass
class JobState(TableModel):
    id: int
    job_name: str
    state: str
    updated_on: int
    
    @staticmethod
    def get_create_table_command():
        return """CREATE TABLE IF NOT EXISTS job_states(
            id INTEGER PRIMARY KEY,
            job_name TEXT NOT NULL UNIQUE,
            state TEXT NOT NULL,
            updated_on INTEGER NOT NULL
        )"""


    
all_tables : list[type[TableModel]] = [
    Player, FriendCode, User, UserDiscord, Role, Permission, UserRole, RolePermission, 
    TournamentSeries, Tournament, TournamentTemplate, TournamentRegistration, TournamentPlayer,
    TournamentPlacements, Team, TeamRoster, TeamMember,
    TeamSquadRegistration, TeamRole, TeamPermission, TeamRolePermission, UserTeamRole,
    SeriesRole, SeriesPermission, SeriesRolePermission, UserSeriesRole, 
    TournamentRole, TournamentPermission, TournamentRolePermission, UserTournamentRole,
    TeamTransfer, TeamEdit, RosterEdit, FriendCodeEdit,
    UserSettings, Notifications, PlayerBans, PlayerBansHistorical,
    PlayerNameEdit, PlayerClaim, FilteredWords,
    Post, SeriesPost, TournamentPost, JobState]
