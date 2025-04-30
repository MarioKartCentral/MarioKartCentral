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
        return """CREATE INDEX IF NOT EXISTS tournament_squads_tournament_id
            ON tournament_squads (tournament_id)"""
    
@dataclass
class TournamentPlayersTournamentIDSquadID(IndexModel):
    @staticmethod
    def get_create_index_command() -> str:
        return """CREATE INDEX IF NOT EXISTS tournament_players_tournament_id_squad_id
            ON tournament_players (tournament_id, squad_id)"""
    
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
class TournamentSoloPlacementsTournamentID(IndexModel):
    @staticmethod
    def get_create_index_command() -> str:
        return """CREATE INDEX IF NOT EXISTS tournament_solo_placements_tournament_id
            ON tournament_solo_placements(tournament_id)"""
    
@dataclass
class TournamentSquadPlacementsTournamentID(IndexModel):
    @staticmethod
    def get_create_index_command() -> str:
        return """CREATE INDEX IF NOT EXISTS tournament_squad_placements_tournament_id
            ON tournament_squad_placements(tournament_id)"""
    

all_indices : list[type[IndexModel]] = [
    UserRolesExpiresOn, UserTeamRolesExpiresOn, UserSeriesRolesExpiresOn, UserTournamentRolesExpiresOn,
    TournamentSquadsTournamentID, TournamentPlayersTournamentIDSquadID, FriendCodesType, FriendCodesPlayerID,
    TournamentSoloPlacementsTournamentID, TournamentSquadPlacementsTournamentID
]