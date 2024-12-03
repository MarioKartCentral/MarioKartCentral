from abc import ABC, abstractmethod
from dataclasses import dataclass

class IndexModel(ABC):
    @staticmethod
    @abstractmethod
    def get_create_index_command() -> str:
        pass

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
    

all_indices : list[type[IndexModel]] = [
    UserRolesExpiresOn, UserTeamRolesExpiresOn, UserSeriesRolesExpiresOn, UserTournamentRolesExpiresOn
]