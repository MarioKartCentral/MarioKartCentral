from dataclasses import dataclass
from common.data.db.common import IndexModel

@dataclass
class UserRolesExpiresOn(IndexModel):
    @staticmethod
    def get_create_index_command():
        return """CREATE INDEX IF NOT EXISTS idx_user_roles_expires_on 
            ON user_roles (expires_on) WHERE expires_on IS NOT NULL"""
    
@dataclass
class UserTeamRolesExpiresOn(IndexModel):
    @staticmethod
    def get_create_index_command():
        return """CREATE INDEX IF NOT EXISTS idx_user_team_roles_expires_on 
            ON user_team_roles (expires_on) WHERE expires_on IS NOT NULL"""
    
@dataclass
class UserSeriesRolesExpiresOn(IndexModel):
    @staticmethod
    def get_create_index_command():
        return """CREATE INDEX IF NOT EXISTS idx_user_series_roles_expires_on 
            ON user_series_roles (expires_on) WHERE expires_on IS NOT NULL"""

@dataclass
class UserTournamentRolesExpiresOn(IndexModel):
    @staticmethod
    def get_create_index_command():
        return """CREATE INDEX IF NOT EXISTS idx_user_tournament_roles_expires_on 
            ON user_tournament_roles (expires_on) WHERE expires_on IS NOT NULL"""
    
@dataclass
class TournamentSquadsTournamentID(IndexModel):
    @staticmethod
    def get_create_index_command() -> str:
        return """CREATE INDEX IF NOT EXISTS idx_tournament_registrations_tournament_id
            ON tournament_registrations (tournament_id)"""
    
@dataclass
class TournamentPlayersTournamentIDSquadID(IndexModel):
    @staticmethod
    def get_create_index_command() -> str:
        return """CREATE INDEX IF NOT EXISTS idx_tournament_players_tournament_id_registration_id
            ON tournament_players (tournament_id, registration_id)"""
    
@dataclass
class TournamentPlayersPlayerID(IndexModel):
    @staticmethod
    def get_create_index_command() -> str:
        return """CREATE INDEX IF NOT EXISTS idx_tournament_players_player_id
            ON tournament_players(player_id)"""
    
@dataclass
class FriendCodesType(IndexModel):
    @staticmethod
    def get_create_index_command() -> str:
        return """CREATE INDEX IF NOT EXISTS idx_friend_codes_type
            ON friend_codes(type)"""
    
@dataclass
class FriendCodesPlayerID(IndexModel):
    @staticmethod
    def get_create_index_command() -> str:
        return """CREATE INDEX IF NOT EXISTS idx_friend_codes_player_id
            ON friend_codes (player_id)"""
    
@dataclass
class TournamentSquadPlacementsTournamentID(IndexModel):
    @staticmethod
    def get_create_index_command() -> str:
        return """CREATE INDEX IF NOT EXISTS idx_tournament_placements_tournament_id
            ON tournament_placements(tournament_id)"""
    
@dataclass
class TeamMembersRosterID(IndexModel):
    @staticmethod
    def get_create_index_command() -> str:
        return """CREATE INDEX IF NOT EXISTS idx_team_members_roster_id
            ON team_members(roster_id)"""
    
@dataclass
class UsersPlayerID(IndexModel):
    @staticmethod
    def get_create_index_command() -> str:
        return """CREATE INDEX IF NOT EXISTS idx_users_player_id
            ON users(player_id)"""

@dataclass
class UsersJoinDate(IndexModel):
    @staticmethod
    def get_create_index_command() -> str:
        return """CREATE INDEX IF NOT EXISTS idx_users_join_date
            ON users(join_date)"""

@dataclass
class UserDiscordsDiscordID(IndexModel):
    @staticmethod
    def get_create_index_command() -> str:
        return """CREATE INDEX IF NOT EXISTS idx_user_discords_discord_id
            ON user_discords(discord_id)"""
    
@dataclass
class PlayersName(IndexModel):
    @staticmethod
    def get_create_index_command() -> str:
        return """CREATE INDEX IF NOT EXISTS idx_players_name 
            ON players(name COLLATE NOCASE)"""
    
@dataclass
class PlayersJoinDate(IndexModel):
    @staticmethod
    def get_create_index_command() -> str:
        return """CREATE INDEX IF NOT EXISTS idx_players_join_date
            ON players(join_date DESC)"""

@dataclass
class PlayersVisibility(IndexModel):
    @staticmethod
    def get_create_index_command() -> str:
        return """CREATE INDEX IF NOT EXISTS idx_players_visibility
            ON players(is_hidden, is_shadow, is_banned)"""
    
@dataclass
class PlayersCountry(IndexModel):
    @staticmethod
    def get_create_index_command() -> str:
        return """CREATE INDEX IF NOT EXISTS idx_players_country
            ON players(country_code)"""
    

all_indices : list[type[IndexModel]] = [
    UserRolesExpiresOn,
    UserTeamRolesExpiresOn,
    UserSeriesRolesExpiresOn,
    UserTournamentRolesExpiresOn,
    TournamentSquadsTournamentID,
    TournamentPlayersTournamentIDSquadID,
    FriendCodesType,
    FriendCodesPlayerID,
    TournamentSquadPlacementsTournamentID,
    TeamMembersRosterID,
    UsersPlayerID,
    UsersJoinDate,
    UserDiscordsDiscordID,
    PlayersName,
    PlayersJoinDate,
    PlayersVisibility,
    PlayersCountry
]