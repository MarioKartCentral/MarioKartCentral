from dataclasses import dataclass
from common.data.db.common import IndexModel

@dataclass
class UserRolesExpiresOn(IndexModel):
    @staticmethod
    def get_create_index_command():
        return """CREATE INDEX IF NOT EXISTS user_roles_expires_on 
            ON user_roles (expires_on) WHERE expires_on IS NOT NULL"""
    
@dataclass
class UserTeamRolesExpiresOn(IndexModel):
    @staticmethod
    def get_create_index_command():
        return """CREATE INDEX IF NOT EXISTS user_team_roles_expires_on 
            ON user_team_roles (expires_on) WHERE expires_on IS NOT NULL"""
    
@dataclass
class UserSeriesRolesExpiresOn(IndexModel):
    @staticmethod
    def get_create_index_command():
        return """CREATE INDEX IF NOT EXISTS user_series_roles_expires_on 
            ON user_series_roles (expires_on) WHERE expires_on IS NOT NULL"""

@dataclass
class UserTournamentRolesExpiresOn(IndexModel):
    @staticmethod
    def get_create_index_command():
        return """CREATE INDEX IF NOT EXISTS user_tournament_roles_expires_on 
            ON user_tournament_roles (expires_on) WHERE expires_on IS NOT NULL"""
    
@dataclass
class TournamentSquadsTournamentID(IndexModel):
    @staticmethod
    def get_create_index_command() -> str:
        return """CREATE INDEX IF NOT EXISTS tournament_registrations_tournament_id
            ON tournament_registrations (tournament_id)"""
    
@dataclass
class TournamentPlayersTournamentIDSquadID(IndexModel):
    @staticmethod
    def get_create_index_command() -> str:
        return """CREATE INDEX IF NOT EXISTS tournament_players_tournament_id_registration_id
            ON tournament_players (tournament_id, registration_id)"""
    
@dataclass
class TournamentPlayersPlayerID(IndexModel):
    @staticmethod
    def get_create_index_command() -> str:
        return """CREATE INDEX IF NOT EXISTS tournament_players_player_id
            ON tournament_players(player_id)"""
    
@dataclass
class FriendCodesType(IndexModel):
    @staticmethod
    def get_create_index_command() -> str:
        return """CREATE INDEX IF NOT EXISTS friend_codes_type
            ON friend_codes(type)"""
    
@dataclass
class FriendCodesPlayerID(IndexModel):
    @staticmethod
    def get_create_index_command() -> str:
        return """CREATE INDEX IF NOT EXISTS friend_codes_player_id
            ON friend_codes (player_id)"""
    
@dataclass
class TournamentSquadPlacementsTournamentID(IndexModel):
    @staticmethod
    def get_create_index_command() -> str:
        return """CREATE INDEX IF NOT EXISTS tournament_placements_tournament_id
            ON tournament_placements(tournament_id)"""
    
@dataclass
class TeamMembersRosterID(IndexModel):
    @staticmethod
    def get_create_index_command() -> str:
        return """CREATE INDEX IF NOT EXISTS team_members_roster_id
            ON team_members(roster_id)"""
    
all_indices : list[type[IndexModel]] = [
    UserRolesExpiresOn, UserTeamRolesExpiresOn, UserSeriesRolesExpiresOn, UserTournamentRolesExpiresOn,
    TournamentSquadsTournamentID, TournamentPlayersTournamentIDSquadID, FriendCodesType, FriendCodesPlayerID,
    TournamentSquadPlacementsTournamentID, TeamMembersRosterID
]