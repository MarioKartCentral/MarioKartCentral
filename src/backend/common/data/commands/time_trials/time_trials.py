"""
Time trials CRUD operations using DuckDB.
"""

from dataclasses import dataclass
from typing import List, Optional
import msgspec
from datetime import datetime, timezone

from common.data.commands import Command, save_to_command_log
from common.data.models import Problem
from common.data.duckdb.models import TimeTrial
from common.data.models.time_trials.schemas import TimeTrialData, deserialize_time_trial_data_from_json, serialize_time_trial_data


@save_to_command_log
@dataclass
class CreateTimeTrialCommand(Command[TimeTrial]):
    """Create a new time trial record."""
    
    player_id: str
    game: str
    track: str
    time_ms: int
    data: TimeTrialData
    proof_url: Optional[str] = None
    description: Optional[str] = None
    
    async def handle(self, db_wrapper, s3_wrapper) -> TimeTrial:
        if self.time_ms <= 0:
            raise Problem("Time must be positive", status=400)
        
        if not self.player_id or not self.player_id.strip():
            raise Problem("Player ID is required", status=400)
            
        if not self.track.strip():
            raise Problem("Track is required", status=400)
            
        if not self.game.strip():
            raise Problem("Game is required", status=400)
        
        now = datetime.now(timezone.utc).isoformat()
        time_trial = TimeTrial(
            player_id=self.player_id,
            game=self.game,
            track=self.track,
            time_ms=self.time_ms,
            data=serialize_time_trial_data(self.data),
            proof_url=self.proof_url or "",
            description=self.description or "",
            created_at=now,
            updated_at=now
        )
        
        async with db_wrapper.duckdb.connection() as conn:
            insert_time_trial_query = """
                INSERT INTO time_trials (id, version, player_id, game, track, time_ms, data, proof_url, description, created_at, updated_at)
                VALUES ($id, $version, $player_id, $game, $track, $time_ms, $data, $proof_url, $description, $created_at, $updated_at)
            """
            await conn.execute(insert_time_trial_query, {
                "id": time_trial.id,
                "version": time_trial.version,
                "player_id": time_trial.player_id,
                "game": time_trial.game,
                "track": time_trial.track,
                "time_ms": time_trial.time_ms,
                "data": msgspec.json.encode(time_trial.data).decode(),
                "proof_url": time_trial.proof_url,
                "description": time_trial.description,
                "created_at": time_trial.created_at,
                "updated_at": time_trial.updated_at,
            })
        
        return time_trial


@dataclass
class GetTimeTrialCommand(Command[Optional[TimeTrial]]):
    """Retrieve a specific time trial by ID."""
    
    trial_id: str

    async def handle(self, db_wrapper, s3_wrapper) -> Optional[TimeTrial]:
        if not self.trial_id.strip():
            raise Problem("Trial ID is required", status=400)
            
        async with db_wrapper.duckdb.connection() as conn:
            get_time_trial_query = """
                SELECT id, version, player_id, game, track, time_ms, data, proof_url, description, created_at, updated_at 
                FROM time_trials WHERE id = $trial_id
            """
            async with conn.execute(get_time_trial_query, {"trial_id": self.trial_id}) as cursor:
                row = await cursor.fetchone()
                if row:
                    id, version, player_id, game, track, time_ms, data, proof_url, description, created_at, updated_at = row
                    # Deserialize directly from JSON to the appropriate schema type for the game
                    data_obj = deserialize_time_trial_data_from_json(data, game)
                    return TimeTrial(
                        id=id,
                        version=version,
                        player_id=player_id,
                        game=game,
                        track=track,
                        time_ms=time_ms,
                        data=data_obj,
                        proof_url=proof_url or "",
                        description=description or "",
                        created_at=created_at,
                        updated_at=updated_at
                    )
        return None


@dataclass  
class ListTimeTrialsCommand(Command[List[TimeTrial]]):
    """List time trials with optional filtering and pagination."""
    
    player_id: Optional[str] = None
    game: Optional[str] = None
    track: Optional[str] = None
    cc: Optional[int] = None  # Engine class for games that support it (e.g., MK8DX)
    limit: int = 100
    offset: int = 0

    async def handle(self, db_wrapper, s3_wrapper) -> List[TimeTrial]:
        if self.limit <= 0 or self.limit > 1000:
            raise Problem("Limit must be between 1 and 1000", status=400)
            
        if self.offset < 0:
            raise Problem("Offset must be non-negative", status=400)
        
        list_time_trials_query = """
            SELECT id, version, player_id, game, track, time_ms, data, proof_url, description, created_at, updated_at 
            FROM time_trials 
            WHERE ($player_id IS NULL OR player_id = $player_id)
              AND ($game IS NULL OR game = $game)
              AND ($track IS NULL OR track = $track)
              AND ($cc IS NULL OR json_extract(data, '$.cc') = $cc)
            ORDER BY time_ms ASC, created_at DESC 
            LIMIT $limit OFFSET $offset
        """
        
        params = {
            "player_id": self.player_id,
            "game": self.game,
            "track": self.track,
            "cc": self.cc,
            "limit": self.limit,
            "offset": self.offset
        }
        
        async with db_wrapper.duckdb.connection() as conn:
            async with conn.execute(list_time_trials_query, params) as cursor:
                rows = await cursor.fetchall()
                result = []
                for row in rows:
                    id, version, player_id, game, track, time_ms, data, proof_url, description, created_at, updated_at = row
                    # Deserialize directly from JSON to the appropriate schema type for the game
                    data_obj = deserialize_time_trial_data_from_json(data, game)
                    result.append(TimeTrial(
                        id=id,
                        version=version,
                        player_id=player_id,
                        game=game,
                        track=track,
                        time_ms=time_ms,
                        data=data_obj,
                        proof_url=proof_url or "",
                        description=description or "",
                        created_at=created_at,
                        updated_at=updated_at
                    ))
                return result


@save_to_command_log
@dataclass
class DeleteTimeTrialCommand(Command[bool]):
    """Delete a time trial record."""
    
    trial_id: str
    
    async def handle(self, db_wrapper, s3_wrapper) -> bool:
        if not self.trial_id.strip():
            raise Problem("Trial ID is required", status=400)
            
        async with db_wrapper.duckdb.connection() as conn:
            delete_time_trial_query = "DELETE FROM time_trials WHERE id = $trial_id"
            await conn.execute(delete_time_trial_query, {"trial_id": self.trial_id})
            # DuckDB doesn't return rowcount easily, so we assume success if no exception
            return True
