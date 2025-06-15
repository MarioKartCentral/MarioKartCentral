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
    """Time trial record with embedded proofs and validation data."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    version: int = 1
    player_id: int = -1  # Foreign key to players table (potentially in a different DB)
    game: str = ""
    track: str = ""
    time_ms: int = 0
    proofs: List[Any] = field(default_factory=list)  # JSON array of proof objects
    is_invalid: bool = False  # Whether the record has been marked as invalid
    validation_status: str = "proofless"  # Precomputed: "valid", "invalid", "unvalidated", "proofless"
    created_at: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    @staticmethod
    def get_create_table_command() -> str:
        return '''
        CREATE TABLE IF NOT EXISTS time_trials (
            id VARCHAR PRIMARY KEY,
            version INTEGER NOT NULL,
            player_id INTEGER NOT NULL,
            game VARCHAR NOT NULL,
            track VARCHAR NOT NULL,
            time_ms INTEGER NOT NULL,
            proofs JSON NOT NULL DEFAULT '[]',
            is_invalid BOOLEAN NOT NULL DEFAULT false,
            validation_status VARCHAR NOT NULL DEFAULT 'proofless',
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_time_trials_game_track_validation_status_time ON time_trials(game, track, validation_status, time_ms);
        CREATE INDEX IF NOT EXISTS idx_time_trials_game_track_player_id_time ON time_trials(game, track, player_id, time_ms);
        CREATE INDEX IF NOT EXISTS idx_time_trials_validation_status ON time_trials(validation_status);
        '''


# Registry of all DuckDB table models for schema setup
ALL_DUCKDB_TABLES = [
    TimeTrial,
]