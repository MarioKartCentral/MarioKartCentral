"""
Leaderboard and statistics queries for time trials using DuckDB.

Commands for complex leaderboard queries and proof validation workflows.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from common.data.commands import Command
from common.data.models import Problem


@dataclass
class GetFastestValidatedTimesByTrackCommand(Command[List[Dict[str, Any]]]):
    """Get fastest validated times per player for a specific track and property."""
    
    track: str
    property_name: str  # e.g. 'character', 'vehicle', etc.
    game: Optional[str] = None
    limit: int = 50

    async def handle(self, db_wrapper, s3_wrapper) -> List[Dict[str, Any]]:
        if not self.track.strip():
            raise Problem("Track is required", status=400)
            
        if not self.property_name.strip():
            raise Problem("Property name is required", status=400)
            
        if self.limit <= 0 or self.limit > 500:
            raise Problem("Limit must be between 1 and 500", status=400)

        # Query for fastest validated times
        leaderboard_validated_query = """
        WITH validated_proofs AS (
            SELECT p.time_trial_id, p.properties, pv.staff_id, pv.is_valid
            FROM proofs p
            JOIN proof_validations pv ON pv.proof_id = p.id
            WHERE pv.is_valid = TRUE AND pv.staff_id IS NOT NULL
        ),
        trials_with_validated_property AS (
            SELECT tt.*, vp.staff_id
            FROM time_trials tt
            JOIN validated_proofs vp ON vp.time_trial_id = tt.id
            WHERE tt.track = $track
              AND JSON_EXTRACT_STRING(vp.properties, '$[*]') LIKE '%' || $property_name || '%'
        ),
        ranked AS (
            SELECT *, ROW_NUMBER() OVER (PARTITION BY player_id ORDER BY time_ms ASC) as rn
            FROM trials_with_validated_property
            WHERE ($game IS NULL OR game = $game)
        )
        SELECT id, player_id, game, track, time_ms, data, created_at, staff_id
        FROM ranked 
        WHERE rn = 1 
        ORDER BY time_ms ASC 
        LIMIT $limit
        """
        
        query_params = {
            "track": self.track,
            "property_name": self.property_name,
            "game": self.game,
            "limit": self.limit
        }
        
        async with db_wrapper.duckdb.connection() as conn:
            async with conn.execute(leaderboard_validated_query, query_params) as cursor:
                rows = await cursor.fetchall()
                results = []
                for row in rows:
                    id, player_id, game, track, time_ms, data, created_at, staff_id = row
                    results.append({
                        'id': id,
                        'player_id': player_id, 
                        'game': game,
                        'track': track,
                        'time_ms': time_ms,
                        'data': data,
                        'created_at': created_at,
                        'validated_by_staff': staff_id
                    })
                return results


@dataclass
class GetTrackLeaderboardCommand(Command[List[Dict[str, Any]]]):
    """Get leaderboard for a specific track with optional game filtering."""
    
    track: str
    game: Optional[str] = None
    limit: int = 100
    include_unvalidated: bool = True
    
    async def handle(self, db_wrapper, s3_wrapper) -> List[Dict[str, Any]]:
        if not self.track.strip():
            raise Problem("Track is required", status=400)
            
        if self.limit <= 0 or self.limit > 500:
            raise Problem("Limit must be between 1 and 500", status=400)
        
        if self.include_unvalidated:
            # Simple leaderboard without validation requirements
            track_leaderboard_query = """
            WITH ranked_times AS (
                SELECT *, ROW_NUMBER() OVER (PARTITION BY player_id ORDER BY time_ms ASC) as rn
                FROM time_trials
                WHERE track = $track AND ($game IS NULL OR game = $game)
            )
            SELECT id, player_id, game, track, time_ms, data, created_at
            FROM ranked_times
            WHERE rn = 1
            ORDER BY time_ms ASC
            LIMIT $limit
            """
            query_params = {
                "track": self.track,
                "game": self.game,
                "limit": self.limit
            }
        else:
            # Only include validated times
            track_leaderboard_query = """
            WITH validated_trials AS (
                SELECT DISTINCT tt.id, tt.player_id, tt.game, tt.track, tt.time_ms, tt.data, tt.created_at
                FROM time_trials tt
                JOIN proofs p ON p.time_trial_id = tt.id
                JOIN proof_validations pv ON pv.proof_id = p.id
                WHERE pv.is_valid = TRUE 
                  AND tt.track = $track 
                  AND ($game IS NULL OR tt.game = $game)
            ),
            ranked_validated AS (
                SELECT *, ROW_NUMBER() OVER (PARTITION BY player_id ORDER BY time_ms ASC) as rn
                FROM validated_trials
            )
            SELECT id, player_id, game, track, time_ms, data, created_at
            FROM ranked_validated
            WHERE rn = 1
            ORDER BY time_ms ASC
            LIMIT $limit
            """
            query_params = {
                "track": self.track,
                "game": self.game,
                "limit": self.limit
            }
        
        async with db_wrapper.duckdb.connection() as conn:
            async with conn.execute(track_leaderboard_query, query_params) as cursor:
                rows = await cursor.fetchall()
                results = []
                for row in rows:
                    id, player_id, game, track, time_ms, data, created_at = row
                    results.append({
                        'id': id,
                        'player_id': player_id,
                        'game': game, 
                        'track': track,
                        'time_ms': time_ms,
                        'data': data,
                        'created_at': created_at
                    })
                return results


@dataclass
class GetPlayerStatsCommand(Command[Dict[str, Any]]):
    """Get comprehensive statistics for a specific player."""
    
    player_id: str
    
    async def handle(self, db_wrapper, s3_wrapper) -> Dict[str, Any]:
        if not self.player_id.strip():
            raise Problem("Player ID is required", status=400)
        
        # Multiple aggregation queries for player statistics
        player_stats_query = """
        WITH player_times AS (
            SELECT * FROM time_trials WHERE player_id = $player_id
        )
        SELECT 
            COUNT(*) as total_times,
            COUNT(DISTINCT track) as unique_tracks,
            COUNT(DISTINCT game) as games_played,
            AVG(time_ms) as avg_time_ms,
            MIN(time_ms) as best_time_ms,
            MAX(time_ms) as worst_time_ms
        FROM player_times
        """
        
        validated_stats_query = """
        WITH validated_times AS (
            SELECT pt.*
            FROM time_trials pt
            JOIN proofs p ON p.time_trial_id = pt.id  
            JOIN proof_validations pv ON pv.proof_id = p.id
            WHERE pv.is_valid = TRUE AND pt.player_id = $player_id
        )
        SELECT COUNT(*) as validated_times_count
        FROM validated_times
        """
        
        query_params = {"player_id": self.player_id}
        
        async with db_wrapper.duckdb.connection() as conn:
            # Get general stats
            async with conn.execute(player_stats_query, query_params) as cursor:
                stats_row = await cursor.fetchone()
                
            # Get validation stats  
            async with conn.execute(validated_stats_query, query_params) as cursor:
                validation_row = await cursor.fetchone()
                
            if not stats_row:
                return {
                    'player_id': self.player_id,
                    'total_times': 0,
                    'unique_tracks': 0,
                    'games_played': 0,
                    'validated_times': 0,
                    'avg_time_ms': None,
                    'best_time_ms': None,
                    'worst_time_ms': None
                }
                
            total_times, unique_tracks, games_played, avg_time_ms, best_time_ms, worst_time_ms = stats_row
                
            if total_times == 0:
                return {
                    'player_id': self.player_id,
                    'total_times': 0,
                    'unique_tracks': 0,
                    'games_played': 0,
                    'validated_times': 0,
                    'avg_time_ms': None,
                    'best_time_ms': None,
                    'worst_time_ms': None
                }
                
            if validation_row:
                validated_times_count, = validation_row
            else:
                validated_times_count = 0
                
            return {
                'player_id': self.player_id,
                'total_times': total_times,
                'unique_tracks': unique_tracks, 
                'games_played': games_played,
                'validated_times': validated_times_count,
                'avg_time_ms': float(avg_time_ms) if avg_time_ms else None,
                'best_time_ms': best_time_ms,
                'worst_time_ms': worst_time_ms
            }
