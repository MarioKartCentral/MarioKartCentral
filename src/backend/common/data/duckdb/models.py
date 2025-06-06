"""
DuckDB models for time trials data storage.

These models define the data structures used in DuckDB for time trials,
proofs, and validation records.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, List
import uuid
import datetime


class DuckDBTableModel(ABC):
    """Base class for DuckDB table models with schema definition capability."""
    
    @staticmethod
    @abstractmethod
    def get_create_table_command() -> str:
        """Return the SQL command to create this table and its indexes."""
        pass


@dataclass
class TimeTrial(DuckDBTableModel):
    """Time trial record with game-specific structured data."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    version: int = 1
    player_id: str = ""
    game: str = ""
    track: str = ""
    time_ms: int = 0
    data: Any = field(default_factory=dict)  # Game-specific structured data (see schemas.py)
    proof_url: str = ""  # Optional URL to proof of the time trial
    description: str = ""  # Optional description/notes about the run
    created_at: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    @staticmethod
    def get_create_table_command() -> str:
        return '''
        CREATE TABLE IF NOT EXISTS time_trials (
            id VARCHAR PRIMARY KEY,
            version INTEGER NOT NULL,
            player_id VARCHAR NOT NULL,
            game VARCHAR NOT NULL,
            track VARCHAR NOT NULL,
            time_ms INTEGER NOT NULL,
            data JSON NOT NULL,
            proof_url VARCHAR,
            description TEXT,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_time_trials_track ON time_trials(track);
        CREATE INDEX IF NOT EXISTS idx_time_trials_player_id ON time_trials(player_id);
        CREATE INDEX IF NOT EXISTS idx_time_trials_time_ms ON time_trials(time_ms);
        CREATE INDEX IF NOT EXISTS idx_time_trials_game_track ON time_trials(game, track);
        '''


@dataclass
class Proof(DuckDBTableModel):
    """Evidence submission for time trial validation."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    time_trial_id: str = ""
    properties: List[str] = field(default_factory=list)  # List of JSON property names this proof validates
    proof_data: Any = field(default_factory=dict)  # JSON-serializable dict (e.g., URL, metadata)
    created_at: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    @staticmethod
    def get_create_table_command() -> str:
        return '''
        CREATE TABLE IF NOT EXISTS proofs (
            id VARCHAR PRIMARY KEY,
            time_trial_id VARCHAR NOT NULL,
            properties JSON NOT NULL,
            proof_data JSON NOT NULL,
            created_at TIMESTAMP NOT NULL,
            FOREIGN KEY(time_trial_id) REFERENCES time_trials(id)
        );
        CREATE INDEX IF NOT EXISTS idx_proofs_time_trial_id ON proofs(time_trial_id);
        '''


@dataclass
class ProofValidation(DuckDBTableModel):
    """Staff validation of submitted proof evidence."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    proof_id: str = ""
    staff_id: str = ""
    is_valid: bool = False
    validated_at: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    notes: str = ""

    @staticmethod
    def get_create_table_command() -> str:
        return '''
        CREATE TABLE IF NOT EXISTS proof_validations (
            id VARCHAR PRIMARY KEY,
            proof_id VARCHAR NOT NULL,
            staff_id VARCHAR NOT NULL,
            is_valid BOOLEAN NOT NULL,
            validated_at TIMESTAMP NOT NULL,
            notes TEXT,
            FOREIGN KEY(proof_id) REFERENCES proofs(id)
        );
        CREATE INDEX IF NOT EXISTS idx_proof_validations_proof_id ON proof_validations(proof_id);
        CREATE INDEX IF NOT EXISTS idx_proof_validations_staff_id ON proof_validations(staff_id);
        '''


# Registry of all DuckDB table models for schema setup
ALL_DUCKDB_TABLES = [
    TimeTrial,
    Proof,
    ProofValidation,
]