from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timezone
import msgspec
import uuid
from common.data.commands import Command, save_to_command_log
from common.data.db.db_wrapper import DBWrapper
from common.data.models import *
from common.data.models import Problem
from common.data.duckdb.models import TimeTrial
from common.data.models.time_trials_api import (
    ProofRequestData,
    ProofWithValidationStatusResponseData,
    ListProofsForValidationResponseData,
    PlayerRecordResponseData,
    ListPlayerRecordsResponseData,
    ProofResponseData,
)
from common.data.s3 import S3Wrapper


def calculate_validation_status(proofs_data: List[Dict[str, Any]], is_invalid: bool = False) -> str:
    """
    Calculate the validation status for a time trial record based on the new logic:
    - valid: there exists a proof with status "valid" 
    - invalid: is_invalid is true OR has proofs but all are marked "invalid"
    - unvalidated: there exists a proof with status "unvalidated", but no proof with status "valid"
    - proofless: there are no proofs at all
    """
    # 1. If record is marked invalid, always return "invalid"
    if is_invalid:
        return "invalid"
    
    # 2. If no proofs at all, return "proofless"
    if not proofs_data:
        return "proofless"
    
    # 3. If any proof has status "valid", return "valid"
    for proof in proofs_data:
        proof_status = proof.get("status", "unvalidated")
        if proof_status == "valid":
            return "valid"
    
    # 4. If any proof has status "unvalidated" (and no valid proofs), return "unvalidated"  
    for proof in proofs_data:
        proof_status = proof.get("status", "unvalidated")
        if proof_status == "unvalidated":
            return "unvalidated"
    
    # 5. If we have proofs but all are "invalid", return "invalid" (not proofless)
    return "invalid"


@dataclass
class CreateTimeTrialCommand(Command[TimeTrial]):
    player_id: int  # Changed from str to int to match database schema
    game: str
    track: str
    time_ms: int
    proofs: List[ProofRequestData] = field(default_factory=list)
    
    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper) -> TimeTrial:
        # Input validation following established patterns
        if self.time_ms <= 0:
            raise Problem("Time must be positive", status=400)
        
        if self.player_id <= 0:  # Changed from string validation to integer validation
            raise Problem("Player ID is required", status=400)
            
        track = self.track.strip()
        if not track:
            raise Problem("Track is required", status=400)
            
        game = self.game.strip()
        if not game:
            raise Problem("Game is required", status=400)
        
        # Validate proof data with clear error messages
        for i, proof in enumerate(self.proofs):
            if not proof.url.strip():
                raise Problem(f"Proof {i + 1}: URL is required", status=400)
            if not proof.type.strip():
                raise Problem(f"Proof {i + 1}: Type is required", status=400)
            # MVP: No property validation required - proofs just need URL and type
        # Create time trial entity with embedded proofs
        now = datetime.now(timezone.utc).isoformat()
        
        # Convert proofs to JSON structure
        proofs_data = []
        for proof_request in self.proofs:
            proof_data = {
                "id": str(uuid.uuid4()),
                "url": proof_request.url.strip(),
                "type": proof_request.type.strip(),
                "status": "unvalidated",
                "created_at": now
            }
            proofs_data.append(proof_data)
        
        # Calculate initial validation status
        initial_validation_status = calculate_validation_status(proofs_data, is_invalid=False)
        
        time_trial = TimeTrial(
            player_id=self.player_id,  # Now using integer directly
            game=game,
            track=track,
            time_ms=self.time_ms,
            proofs=proofs_data,
            is_invalid=False,
            validation_status=initial_validation_status,
            created_at=now,
            updated_at=now
        )

        async with db_wrapper.duckdb.connection() as conn:
            # Insert time trial record with embedded proofs and validation status
            insert_time_trial_query = """
                INSERT INTO time_trials (id, version, player_id, game, track, time_ms, proofs, is_invalid, validation_status, created_at, updated_at)
                VALUES ($id, $version, $player_id, $game, $track, $time_ms, $proofs, $is_invalid, $validation_status, $created_at, $updated_at)
            """
            await conn.execute(insert_time_trial_query, {
                "id": time_trial.id,
                "version": time_trial.version,
                "player_id": time_trial.player_id,
                "game": time_trial.game,
                "track": time_trial.track,
                "time_ms": time_trial.time_ms,
                "proofs": msgspec.json.encode(time_trial.proofs).decode(),
                "is_invalid": time_trial.is_invalid,
                "validation_status": time_trial.validation_status,
                "created_at": time_trial.created_at,
                "updated_at": time_trial.updated_at,
            })
        
        return time_trial


@dataclass
class GetTimeTrialCommand(Command[Optional[TimeTrial]]):
    """Retrieve a specific time trial by ID."""
    
    trial_id: str

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper) -> Optional[TimeTrial]:
        if not self.trial_id.strip():
            raise Problem("Trial ID is required", status=400)

        async with db_wrapper.duckdb.connection() as conn:
            # Retrieve time trial record with embedded proofs
            get_time_trial_query = """
                SELECT id, version, player_id, game, track, time_ms, proofs, created_at, updated_at 
                FROM time_trials WHERE id = $trial_id
            """
            async with conn.execute(get_time_trial_query, {"trial_id": self.trial_id}) as cursor:
                row = await cursor.fetchone()
                if row:
                    id, version, player_id, game, track, time_ms, proofs_json, created_at, updated_at = row
                    proofs_obj = msgspec.json.decode(proofs_json) if proofs_json else []
                    
                    return TimeTrial(
                        id=id,
                        version=version,
                        player_id=player_id,
                        game=game,
                        track=track,
                        time_ms=time_ms,
                        proofs=proofs_obj,
                        created_at=created_at,
                        updated_at=updated_at
                    )
        return None


@dataclass  
class ListTimeTrialsCommand(Command[List[Tuple[TimeTrial, Optional[str], Optional[str]]]]): 
    """List time trials with optional filtering and pagination, joining player data from SQLite."""
    
    player_id: Optional[str] = None
    game: Optional[str] = None
    track: Optional[str] = None
    limit: int = 100
    offset: int = 0

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper) -> List[Tuple[TimeTrial, Optional[str], Optional[str]]]:
        # Input validation following established patterns
        if self.limit <= 0 or self.limit > 1000:
            raise Problem("Limit must be between 1 and 1000", status=400)
            
        if self.offset < 0:
            raise Problem("Offset must be non-negative", status=400)
        
        # Get the path to the main SQLite database from the db_wrapper
        main_sqlite_db_path = db_wrapper.db_paths.get('main')
        if not main_sqlite_db_path:
            raise Problem("Main SQLite database not configured", status=500)
        sqlite_db_alias = "main_sqlite_db"  # Alias for the attached SQLite DB

        # DuckDB + SQLite join query - this is the efficient pattern we want to preserve
        list_time_trials_query = f"""
            INSTALL sqlite;
            LOAD sqlite;
            ATTACH '{main_sqlite_db_path}' AS {sqlite_db_alias} (READ_ONLY);

            SELECT 
                tt.id, tt.version, tt.player_id, tt.game, tt.track, tt.time_ms, tt.proofs, tt.created_at, tt.updated_at,
                p.name AS player_name, p.country_code AS player_country_code
            FROM time_trials tt
            LEFT JOIN {sqlite_db_alias}.players p ON tt.player_id = p.id
            WHERE ($player_id_param IS NULL OR tt.player_id = $player_id_param)
              AND ($game_param IS NULL OR tt.game = $game_param)
              AND ($track_param IS NULL OR tt.track = $track_param)
              AND (tt.is_invalid = false)
            ORDER BY tt.time_ms ASC, tt.created_at DESC 
            LIMIT $limit_param OFFSET $offset_param
        """
        
        params = {
            "player_id_param": self.player_id,
            "game_param": self.game,
            "track_param": self.track,
            "limit_param": self.limit,
            "offset_param": self.offset
        }
        
        results: List[Tuple[TimeTrial, Optional[str], Optional[str]]] = []

        async with db_wrapper.duckdb.connection() as conn:
            # Execute the DuckDB + SQLite join query
            # Note: INSTALL and LOAD might be better handled globally at application startup
            # for better performance, but including them ensures they are run for each query
            async with conn.execute(list_time_trials_query, params) as cursor:
                rows = await cursor.fetchall()
                
                for row_data in rows:
                    (id_val, version_val, player_id_val, game_val, track_val, time_ms_val, 
                     proofs_json, created_at_val, updated_at_val, player_name_val, player_country_code_val) = row_data
                    
                    proofs_obj = msgspec.json.decode(proofs_json) if proofs_json else []
                    
                    # Filter out invalid proofs from display
                    filtered_proofs = []
                    for proof in proofs_obj:
                        proof_status = proof.get("status", "unvalidated")  # Default for migration
                        if proof_status != "invalid":
                            filtered_proofs.append(proof)
                    
                    # Create TimeTrial instance from DuckDB data with filtered proofs
                    time_trial_item = TimeTrial(
                        id=id_val,
                        version=version_val,
                        player_id=player_id_val,
                        game=game_val,
                        track=track_val,
                        time_ms=time_ms_val,
                        proofs=filtered_proofs,
                        created_at=created_at_val,
                        updated_at=updated_at_val
                    )
                    
                    results.append((time_trial_item, player_name_val, player_country_code_val))
        return results


@dataclass
class MarkProofInvalidCommand(Command[Dict[str, Any]]):
    """Mark an entire proof as invalid"""
    
    time_trial_id: str
    proof_id: str
    validated_by_player_id: str

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper) -> Dict[str, Any]:
        # Input validation
        if not self.proof_id.strip():
            raise Problem("Proof ID is required", status=400)
        if not self.validated_by_player_id.strip():
            raise Problem("Validator player ID is required", status=400)
            
        now_iso = datetime.now(timezone.utc).isoformat()

        async with db_wrapper.duckdb.connection() as conn:
            # Find the time trial that contains this proof_id in its embedded proofs
            find_trial_query = """
                SELECT proofs, is_invalid 
                FROM time_trials 
                WHERE id = $trial_id
            """
            async with conn.execute(find_trial_query, {"trial_id": self.time_trial_id}) as cursor:
                trial_rows = await cursor.fetchone()
                if not trial_rows:
                    raise Problem(f"Time trial with ID {self.time_trial_id} not found", status=404)
            
            # Parse the JSON string to get the actual proofs data
            proofs_json, is_invalid = trial_rows
            if is_invalid:
                raise Problem(f"Time trial {self.time_trial_id} is marked as invalid", status=400)
            
            proofs_data = msgspec.json.decode(proofs_json) if proofs_json else []

            proof_data = None
            for proof in proofs_data:
                if proof.get("id") == self.proof_id:
                    proof_data = proof
                    break
            
            if proof_data is None:
                raise Problem(f"Proof with id {self.proof_id} not found in time trial {self.time_trial_id}", status=404)

            proof_data["status"] = "invalid"
            proof_data["validator_id"] = self.validated_by_player_id
            proof_data["validated_at"] = now_iso

            new_validation_status = calculate_validation_status(proofs_data, is_invalid=False)
            print(f"New validation status after marking proof valid: {new_validation_status}")
            print(proofs_data)

            update_trial_query = "UPDATE time_trials SET proofs = $proofs, validation_status = $validation_status WHERE id = $time_trial_id"
            await conn.execute(update_trial_query, {
                "proofs": msgspec.json.encode(proofs_data).decode(),
                "validation_status": new_validation_status,
                "time_trial_id": self.time_trial_id
            })

        return {
            "proof_id": self.proof_id,
            "marked_invalid": True,
            "validated_at": now_iso,
            "validated_by_player_id": self.validated_by_player_id,
            "new_validation_status": new_validation_status
        }


@dataclass
class MarkProofValidCommand(Command[Dict[str, Any]]):
    """Mark an entire proof as valid (validates both track and time for MVP)."""
    
    time_trial_id: str
    proof_id: str
    validated_by_player_id: str

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper) -> Dict[str, Any]:
        # Input validation
        if not self.proof_id.strip():
            raise Problem("Proof ID is required", status=400)
        if not self.validated_by_player_id.strip():
            raise Problem("Validator player ID is required", status=400)
            
        now_iso = datetime.now(timezone.utc).isoformat()

        async with db_wrapper.duckdb.connection() as conn:
            # Find the time trial that contains this proof_id in its embedded proofs
            find_trial_query = """
                SELECT proofs, is_invalid 
                FROM time_trials 
                WHERE id = $time_trial_id
            """
            async with conn.execute(find_trial_query, {"time_trial_id": self.time_trial_id}) as cursor:
                trial_rows = await cursor.fetchone()
                if not trial_rows:
                    raise Problem(f"Time trial with ID {self.time_trial_id} not found", status=404)
            
            # Parse the JSON string to get the actual proofs data
            proofs_json, is_invalid = trial_rows
            if is_invalid:
                raise Problem(f"Time trial {self.time_trial_id} is marked as invalid", status=400)

            proofs_data = msgspec.json.decode(proofs_json) if proofs_json else []

            # Find the specific proof in the proofs data
            proof_data = None
            for proof in proofs_data:
                if proof.get("id") == self.proof_id:
                    proof_data = proof
                    break
            
            if proof_data is None:
                raise Problem(f"Proof with id {self.proof_id} not found in time trial {self.time_trial_id}", status=404)

            # Mark the proof as valid with simplified status structure
            proof_data["status"] = "valid"
            proof_data["validator_id"] = self.validated_by_player_id
            proof_data["validated_at"] = now_iso

            new_validation_status = calculate_validation_status(proofs_data, is_invalid=False)
            print(f"New validation status after marking proof valid: {new_validation_status}")
            print(proofs_data)
            
            # Update the time trial with the modified proofs
            update_trial_query = "UPDATE time_trials SET proofs = $proofs, validation_status = $validation_status WHERE id = $time_trial_id"
            await conn.execute(update_trial_query, {
                "proofs": msgspec.json.encode(proofs_data).decode(),
                "time_trial_id": self.time_trial_id,
                "validation_status": new_validation_status
            })

        return {
            "proof_id": self.proof_id,
            "marked_valid": True,
            "validated_at": now_iso,
            "validated_by_player_id": self.validated_by_player_id,
            "new_validation_status": new_validation_status
        }


@dataclass
class ListProofsForValidationCommand(Command[ListProofsForValidationResponseData]):
    """List all proofs with their validation statuses."""
    
    async def handle(self, db_wrapper, s3_wrapper) -> ListProofsForValidationResponseData:
        response_proofs: List[ProofWithValidationStatusResponseData] = []

        # Get the path to the main SQLite database from the db_wrapper
        main_sqlite_db_path = db_wrapper.db_paths.get('main')
        if not main_sqlite_db_path:
            raise Problem("Main SQLite database not configured", status=500)
        sqlite_db_alias = "main_sqlite_db"  # Alias for the attached SQLite DB

        async with db_wrapper.duckdb.connection() as conn:
            # DuckDB + SQLite join query to get time trials with player information
            get_all_time_trials_query = f"""
                INSTALL sqlite;
                LOAD sqlite;
                ATTACH '{main_sqlite_db_path}' AS {sqlite_db_alias} (READ_ONLY);

                SELECT 
                    tt.id, tt.player_id, tt.game, tt.track, tt.time_ms, tt.proofs,
                    p.name AS player_name,
                    p.country_code AS player_country_code
                FROM time_trials tt
                LEFT JOIN {sqlite_db_alias}.players p ON tt.player_id = p.id
                WHERE tt.validation_status = 'unvalidated' AND tt.is_invalid = false
                ORDER BY tt.created_at DESC
            """

            async with conn.execute(get_all_time_trials_query) as cursor:
                all_trial_rows = await cursor.fetchall()

        # Process time trials with player information
        results: List[ProofWithValidationStatusResponseData] = []
        
        for trial_row in all_trial_rows:
            tt_id, tt_player_id, tt_game, tt_track, tt_time_ms, tt_proofs_json, player_name, player_country_code = trial_row
            
            try:
                # Parse embedded proofs
                proofs_data = msgspec.json.decode(tt_proofs_json) if tt_proofs_json else []
            except msgspec.DecodeError:
                # Skip malformed time trial records
                print(f"Error decoding JSON for time_trial_id {tt_id}")
                continue

            # Process each proof in this time trial
            for proof_data in proofs_data:
                p_id = proof_data.get("id")
                if not p_id:
                    continue
                    
                # MVP: No properties tracking needed
                proof_data_dict = {
                    "url": proof_data.get("url", ""),
                    "type": proof_data.get("type", "")
                }
                p_created_at = proof_data.get("created_at", "")
                proof_status = proof_data.get("status", "unvalidated")  # Default to unvalidated for migration

                # Check if this proof should be excluded from validation queue
                should_include_proof = True
                
                # 1. Skip proofs that are already validated (valid or invalid)
                if proof_status in ["valid", "invalid"]:
                    should_include_proof = False
                
                # Skip this proof if it shouldn't be included
                if not should_include_proof:
                    continue

                # MVP: Simplified validation status - no individual properties to track
                # For MVP, we don't track individual properties - just whether the proof needs validation
                # The proof either needs validation (unvalidated) or doesn't (already valid/invalid)
                
                response_proofs.append(
                    ProofWithValidationStatusResponseData(
                        id=p_id,
                        time_trial_id=tt_id,
                        player_id=tt_player_id,
                        player_name=player_name,
                        player_country_code=player_country_code,
                        game=tt_game,
                        proof_data=proof_data_dict,
                        properties=[],  # MVP: No properties tracking
                        created_at=p_created_at,
                        track=tt_track,
                        time_ms=tt_time_ms,
                    )
                )
            
        return ListProofsForValidationResponseData(proofs=response_proofs)


@dataclass
class EditTimeTrialPropertiesCommand(Command[Dict[str, Any]]):
    """Command to edit properties of a time trial and reset validation status for changed properties."""
    
    time_trial_id: str
    user_id: str
    track: Optional[str] = None
    time_ms: Optional[int] = None

    def validate(self):
        """Validate the input parameters."""
        if not self.time_trial_id or not self.time_trial_id.strip():
            raise Problem("Time trial ID is required", status=400)
        
        if not self.user_id or not self.user_id.strip():
            raise Problem("User ID is required", status=400)
            
        if self.time_ms is not None and self.time_ms <= 0:
            raise Problem("Time must be positive", status=400)
            
        # Check that at least one property is being edited
        if self.track is None and self.time_ms is None:
            raise Problem("At least one property must be specified for editing", status=400)

    async def handle(self, db_wrapper, s3_wrapper) -> Dict[str, Any]:
        """Execute the command to edit time trial properties."""
        self.validate()
        
        async with db_wrapper.duckdb.connection() as conn:
            # First, get the current time trial
            get_query = """
                SELECT id, version, player_id, game, track, time_ms, proofs, created_at, updated_at 
                FROM time_trials 
                WHERE id = ?
            """
            result = await conn.execute(get_query, [self.time_trial_id])
            row = await result.fetchone()
            
            if not row:
                raise Problem(f"Time trial with ID {self.time_trial_id} not found", status=404)
            trial_id, version, player_id, game, current_track, current_time_ms, proofs_json, created_at, _ = row
            
            # Parse current data and proofs
            proofs_data = msgspec.json.decode(proofs_json) if proofs_json else []
            
            # Prepare updated values
            new_track = self.track if self.track is not None else current_track
            new_time_ms = self.time_ms if self.time_ms is not None else current_time_ms
            
            # Reset validation status for all proofs
            updated_proofs_data = []
            for proof in proofs_data:
                updated_proof = dict(proof)
                updated_proof["status"] = "unvalidated"  # Reset status to unvalidated
                updated_proofs_data.append(updated_proof)
            
            # Update the database
            new_version = version + 1
            update_time = datetime.now(timezone.utc).isoformat()
            
            update_query = """
                UPDATE time_trials 
                SET version = ?, track = ?, time_ms = ?, proofs = ?, updated_at = ?
                WHERE id = ?
            """
            
            await conn.execute(update_query, [
                new_version,
                new_track,
                new_time_ms,
                msgspec.json.encode(updated_proofs_data).decode('utf-8'),
                update_time,
                self.time_trial_id
            ])
            
            # Return the updated time trial data
            return {
                "success": True,
                "id": trial_id,
                "version": new_version,
                "player_id": player_id,
                "game": game,
                "track": new_track,
                "time_ms": new_time_ms,
                "proofs": updated_proofs_data,
                "created_at": created_at,
                "updated_at": update_time,
            }


@dataclass
class ListPlayerRecordsCommand(Command[ListPlayerRecordsResponseData]):
    """List time trial records for a specific player with filtering and sorting."""
    
    player_id: int  # Changed from str to int to match database schema
    game: Optional[str] = None
    track: Optional[str] = None
    show_superseded: bool = False
    sort_by: str = "created_at" 
    sort_order: str = "desc"
    page: int = 1
    page_size: int = 20

    async def handle(self, db_wrapper, s3_wrapper) -> ListPlayerRecordsResponseData:
        """List time trial records for a player with filtering and sorting."""
        
        # Get the path to the main SQLite database from the db_wrapper
        main_sqlite_db_path = db_wrapper.db_paths.get('main')
        if not main_sqlite_db_path:
            raise Problem("Main SQLite database not configured", status=500)
        sqlite_db_alias = "main_sqlite_db"  # Alias for the attached SQLite DB
        
        # Build attach query
        attach_query = f"""
            INSTALL sqlite;
            LOAD sqlite;
            ATTACH '{main_sqlite_db_path}' AS {sqlite_db_alias} (READ_ONLY);
        """
        
        # Build the base query with supersession logic using window functions
        base_query = f"""
            SELECT 
                tt.id, tt.version, tt.player_id, tt.game, tt.track, tt.time_ms, 
                tt.proofs, tt.created_at, tt.updated_at,
                p.name as player_name, p.country_code,
                -- Calculate if this is the player's best time for this track
                CASE WHEN tt.time_ms = MIN(tt.time_ms) OVER (PARTITION BY tt.player_id, tt.game, tt.track) 
                     THEN true ELSE false END as is_current_best,
                -- Get the ID of the record with the best time for this track (for superseded_by)
                FIRST_VALUE(tt.id) OVER (
                    PARTITION BY tt.player_id, tt.game, tt.track 
                    ORDER BY tt.time_ms ASC, tt.created_at ASC
                ) as best_record_id
            FROM time_trials tt
            LEFT JOIN {sqlite_db_alias}.players p ON tt.player_id = p.id
            WHERE tt.player_id = ?
        """
        
        query_params: list[Any] = [self.player_id]
        
        # Add filters
        if self.game:
            base_query += " AND tt.game = ?"
            query_params.append(self.game)
            
        if self.track:
            base_query += " AND tt.track = ?"
            query_params.append(self.track)
        
        # Wrap in subquery to filter superseded records if needed
        if not self.show_superseded:
            base_query = f"""
                SELECT * FROM ({base_query}) subq 
                WHERE subq.is_current_best = true
            """
        
        # Add sorting
        sort_column_map = {
            "created_at": "created_at",
            "track": "track", 
            "time_ms": "time_ms",
            "updated_at": "updated_at"
        }
        
        sort_column = sort_column_map.get(self.sort_by, "created_at")
        sort_direction = "ASC" if self.sort_order == "asc" else "DESC"
        base_query += f" ORDER BY {sort_column} {sort_direction}"
        
        # Add pagination
        offset = (self.page - 1) * self.page_size
        base_query += f" LIMIT {self.page_size} OFFSET {offset}"
        
        # Count total records for pagination (with same filtering)
        count_query = """
            SELECT COUNT(*) as total
            FROM (
                SELECT 
                    tt.id,
                    CASE WHEN tt.time_ms = MIN(tt.time_ms) OVER (PARTITION BY tt.player_id, tt.game, tt.track) 
                         THEN true ELSE false END as is_current_best
                FROM time_trials tt
                WHERE tt.player_id = ?
        """
        count_params: list[Any] = [self.player_id]
        
        if self.game:
            count_query += " AND tt.game = ?"
            count_params.append(self.game)
            
        if self.track:
            count_query += " AND tt.track = ?"
            count_params.append(self.track)
            
        count_query += ") subq"
        
        if not self.show_superseded:
            count_query += " WHERE subq.is_current_best = true"
        
        async with db_wrapper.duckdb.connection() as conn:
            # First execute the attach commands
            await conn.execute(attach_query)
            
            # Get total count
            async with conn.execute(count_query, count_params) as cursor:
                row = await cursor.fetchone()
                total_count = row[0] if row else 0
            
            # Get records
            records = []
            async with conn.execute(base_query, query_params) as cursor:
                async for row in cursor:
                    try:
                        # Unpack the row using tuple unpacking for clarity
                        (id, version, player_id, game, track, time_ms, 
                         proofs_json, created_at, updated_at,
                         player_name, country_code, 
                         is_current_best_raw, best_record_id) = row
                        
                        # Parse proofs JSON and filter out invalid ones
                        proofs_data = msgspec.json.decode(proofs_json) if proofs_json else []
                        proof_responses = []
                        for proof in proofs_data:
                            # Only include proofs that are not marked as invalid
                            proof_status = proof.get("status", "unvalidated")  # Default for migration
                            if proof_status != "invalid":
                                proof_responses.append(ProofResponseData(
                                    id=proof.get('id', ''),
                                    url=proof.get('url', ''),
                                    type=proof.get('type', ''),
                                    created_at=proof.get('created_at', ''),
                                    status=proof_status,
                                    validator_id=proof.get('validator_id'),
                                    validated_at=proof.get('validated_at'),
                                ))
                        
                        # Calculate supersession status
                        is_current_best = bool(is_current_best_raw)
                        is_superseded = not is_current_best
                        superseded_by = best_record_id if is_superseded and best_record_id != id else None
                        
                        # Calculate validation status
                        validation_status = calculate_validation_status(proofs_data)
                        
                        # Create record response
                        record = PlayerRecordResponseData(
                            id=id,
                            version=version,
                            player_id=player_id,
                            game=game,
                            track=track,
                            time_ms=time_ms,
                            proofs=proof_responses,
                            created_at=created_at.isoformat() if hasattr(created_at, 'isoformat') else str(created_at),
                            updated_at=updated_at.isoformat() if hasattr(updated_at, 'isoformat') else str(updated_at),
                            player_name=player_name,
                            country_code=country_code,
                            is_superseded=is_superseded,
                            superseded_by=superseded_by,
                            is_current_best=is_current_best,
                            validation_status=validation_status
                        )
                        records.append(record)
                        
                    except Exception as e:
                        # Skip malformed records but log the error
                        print(f"Error processing record: {e}")
                        continue
            
            # Calculate pagination
            has_next_page = (self.page * self.page_size) < total_count
            
            return ListPlayerRecordsResponseData(
                records=records,
                total_count=total_count,
                page=self.page,
                page_size=self.page_size,
                has_next_page=has_next_page
            )


@dataclass
class GetLeaderboardCommand(Command[List[PlayerRecordResponseData]]):
    """
    New simplified leaderboard command using precomputed validation_status.
    Gets best time per player for a game/track with efficient database filtering.
    """
    
    game: Optional[str] = None
    track: Optional[str] = None
    include_unvalidated: bool = False  # Include records with unvalidated proofs
    include_proofless: bool = False    # Include records without proofs
    limit: int = 50
    offset: int = 0

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper) -> List[PlayerRecordResponseData]:
        """Get leaderboard showing only best times per player using precomputed validation status."""
        
        # Get the path to the main SQLite database from the db_wrapper
        main_sqlite_db_path = db_wrapper.db_paths.get('main')
        if not main_sqlite_db_path:
            raise Problem("Main SQLite database not configured", status=500)
        sqlite_db_alias = "main_sqlite_db"
        
        # Build validation status filter (additive logic)
        validation_filters = ["tt.validation_status = 'valid'"]  # Always include valid
        
        if self.include_unvalidated:
            validation_filters.append("tt.validation_status = 'unvalidated'")
            
        if self.include_proofless:
            validation_filters.append("tt.validation_status = 'proofless'")
        
        # Never include invalid records (tt.validation_status = 'invalid')
        validation_condition = f"({' OR '.join(validation_filters)})"
        
        # Build WHERE conditions
        where_conditions = [validation_condition]
        query_params = {}
        
        if self.game:
            where_conditions.append("tt.game = $game")
            query_params["game"] = self.game
        
        if self.track:
            where_conditions.append("tt.track = $track") 
            query_params["track"] = self.track
            
        where_clause = " AND ".join(where_conditions)
        
        # Simple and efficient query using precomputed validation_status
        query = f"""
            INSTALL sqlite;
            LOAD sqlite;
            ATTACH '{main_sqlite_db_path}' AS {sqlite_db_alias} (READ_ONLY);
            
            WITH player_best_times AS (
                SELECT 
                    player_id, game, track,
                    MIN(time_ms) as best_time_ms
                FROM time_trials tt_inner
                WHERE {where_clause.replace('tt.', 'tt_inner.')} AND tt_inner.is_invalid = false
                GROUP BY player_id, game, track
            )
            SELECT 
                tt.id, tt.version, tt.player_id, tt.game, tt.track, tt.time_ms,
                tt.proofs, tt.created_at, tt.updated_at, tt.validation_status,
                p.name as player_name, p.country_code
            FROM time_trials tt
            INNER JOIN player_best_times pbt ON (
                tt.player_id = pbt.player_id 
                AND tt.game = pbt.game 
                AND tt.track = pbt.track 
                AND tt.time_ms = pbt.best_time_ms
            )
            LEFT JOIN {sqlite_db_alias}.players p ON tt.player_id = p.id
            WHERE {where_clause}
            ORDER BY tt.time_ms ASC, tt.created_at ASC
            LIMIT $limit OFFSET $offset
        """
        
        query_params["limit"] = self.limit
        query_params["offset"] = self.offset

        async with db_wrapper.duckdb.connection() as conn:
            records = []
            async with conn.execute(query, query_params) as cursor:
                async for row in cursor:
                    try:
                        # Parse proofs JSON and filter out invalid ones for response
                        proofs_data = msgspec.json.decode(row[6]) if row[6] else []
                        proof_responses = []
                        for proof in proofs_data:
                            # Only include proofs that are not marked as invalid
                            proof_status = proof.get("status", "unvalidated")
                            if proof_status != "invalid":
                                proof_responses.append(ProofResponseData(
                                    id=proof.get('id', ''),
                                    url=proof.get('url', ''),
                                    type=proof.get('type', ''),
                                    created_at=proof.get('created_at', ''),
                                    status=proof_status,
                                    validator_id=proof.get('validator_id'),
                                    validated_at=proof.get('validated_at'),
                                ))
                        
                        # Create the record (validation_status already computed)
                        record = PlayerRecordResponseData(
                            id=row[0],           # tt.id
                            version=row[1],      # tt.version
                            player_id=row[2],    # tt.player_id
                            game=row[3],         # tt.game
                            track=row[4],        # tt.track
                            time_ms=row[5],      # tt.time_ms
                            proofs=proof_responses,
                            created_at=row[7],   # tt.created_at
                            updated_at=row[8],   # tt.updated_at
                            player_name=row[10], # p.name
                            country_code=row[11], # p.country_code
                            is_superseded=False,
                            superseded_by=None,
                            is_current_best=True,
                            validation_status=row[9] # tt.validation_status (precomputed)
                        )
                        records.append(record)
                        
                    except Exception as e:
                        print(f"Error processing leaderboard record {row[0]}: {e}")
                        continue
            
            return records


@dataclass
class MarkTimeTrialInvalidCommand(Command[Dict[str, Any]]):
    """Mark an entire time trial record as invalid by setting is_invalid=true."""
    
    time_trial_id: str
    validated_by_player_id: str

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper) -> Dict[str, Any]:
        # Input validation
        if not self.time_trial_id.strip():
            raise Problem("Time trial ID is required", status=400)
        if not self.validated_by_player_id.strip():
            raise Problem("Validator player ID is required", status=400)
            
        now_iso = datetime.now(timezone.utc).isoformat()

        async with db_wrapper.duckdb.connection() as conn:
            # Check if the time trial exists
            check_trial_query = """
                SELECT id, is_invalid 
                FROM time_trials 
                WHERE id = $time_trial_id
            """
            async with conn.execute(check_trial_query, {"time_trial_id": self.time_trial_id}) as cursor:
                trial_row = await cursor.fetchone()
                if not trial_row:
                    raise Problem(f"Time trial with ID {self.time_trial_id} not found", status=404)
            
            # Mark the entire time trial as invalid
            update_query = """
                UPDATE time_trials 
                SET is_invalid = true, 
                    validation_status = 'invalid',
                    updated_at = $updated_at
                WHERE id = $time_trial_id
            """
            await conn.execute(update_query, {
                "updated_at": now_iso,
                "time_trial_id": self.time_trial_id
            })

        return {
            "time_trial_id": self.time_trial_id,
            "marked_invalid": True,
            "validated_at": now_iso,
            "validated_by_player_id": self.validated_by_player_id,
            "validation_status": "invalid"
        }
