from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime, timezone
import msgspec
import uuid
from common.data.commands import Command
from common.data.db.db_wrapper import DBWrapper
from common.data.models import *
from common.data.models import Problem
from common.data.duckdb.models import TimeTrial, TimeTrialProof
from common.data.models.time_trials_api import (
    ProofRequestData,
    ProofWithValidationStatusResponseData,
    ListProofsForValidationResponseData,
    TimeTrialResponseData,
    ProofResponseData,
    EditProofDictRequired,
    TimesheetFilter,
)
from common.data.s3 import S3Wrapper


def calculate_validation_status(proofs_data: List[TimeTrialProof], record_is_invalid: bool = False) -> str:
    """
    Calculate the validation status for a time trial record based on the new logic:
    - valid: there exists a proof with status "valid" 
    - invalid: is_invalid is true OR has proofs but all are marked "invalid"
    - unvalidated: there exists a proof with status "unvalidated", but no proof with status "valid"
    - proofless: there are no proofs at all
    """
    # 1. If record is marked invalid, always return "invalid"
    if record_is_invalid:
        return "invalid"
    
    # 2. If no proofs at all, return "proofless"
    if not proofs_data:
        return "proofless"
    
    # 3. If any proof has status "valid", return "valid"
    for proof in proofs_data:
        if proof.status == "valid":
            return "valid"
    
    # 4. If any proof has status "unvalidated" (and no valid proofs), return "unvalidated"  
    for proof in proofs_data:
        if proof.status == "unvalidated":
            return "unvalidated"
    
    # 5. If we have proofs but all are "invalid", return "invalid" (not proofless)
    return "invalid"


@dataclass
class CreateTimeTrialCommand(Command[TimeTrial]):
    player_id: int  # Changed from str to int to match database schema
    game: str
    track: str
    time_ms: int
    proofs: List[ProofRequestData] = field(default_factory=lambda: [])
    
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
        
        for i, proof in enumerate(self.proofs):
            if not proof.url.strip():
                raise Problem(f"Proof {i + 1}: URL is required", status=400)
            if not proof.type.strip():
                raise Problem(f"Proof {i + 1}: Type is required", status=400)
            
        now = datetime.now(timezone.utc).isoformat()
        
        proofs_data: list[TimeTrialProof] = []
        for proof_request in self.proofs:
            proof_data = TimeTrialProof(
                id=str(uuid.uuid4()),
                url=proof_request.url.strip(),
                type=proof_request.type.strip(),
                status="unvalidated",
                created_at=now,
            )
            proofs_data.append(proof_data)
        
        initial_validation_status = calculate_validation_status(proofs_data, record_is_invalid=False)
        
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
class GetTimeTrialCommand(Command[Optional[TimeTrialResponseData]]):
    """Retrieve a specific time trial by ID."""
    
    trial_id: str

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper) -> Optional[TimeTrialResponseData]:
        if not self.trial_id.strip():
            raise Problem("Trial ID is required", status=400)
        
        async with db_wrapper.duckdb.connection() as conn:
            # Retrieve time trial record with embedded proofs
            get_time_trial_query = f"""
                SELECT tt.id, tt.version, tt.player_id, tt.game, tt.track, tt.time_ms, tt.proofs, tt.created_at, tt.updated_at, tt.validation_status
                FROM time_trials tt
                WHERE tt.id = $trial_id
            """
            async with conn.execute(get_time_trial_query, {"trial_id": self.trial_id}) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    return None

        (id, version, player_id, game, track, time_ms, proofs_json, created_at, updated_at, validation_status) = row
        proofs_obj = msgspec.json.decode(proofs_json, type=List[TimeTrialProof]) if proofs_json else []

        player_name, player_country_code = None, None
        async with db_wrapper.connect() as conn:
            player_query = "SELECT name, country_code FROM players WHERE id = :player_id"
            async with conn.execute(player_query, {"player_id": player_id}) as cursor:
                player_row = await cursor.fetchone()
                if player_row:
                    player_name, player_country_code = player_row

        response_proofs = [
            ProofResponseData(
                id=proof.id,
                url=proof.url,
                type=proof.type,
                created_at=proof.created_at,
                status=proof.status,
                validator_id=proof.validator_id,
                validated_at=proof.validated_at,
            )
            for proof in proofs_obj
        ]

        return TimeTrialResponseData(
            id=id,
            version=version,
            player_id=player_id,
            game=game,
            track=track,
            time_ms=time_ms,
            proofs=response_proofs,
            created_at=created_at,
            updated_at=updated_at,
            validation_status=validation_status,
            player_name=player_name,
            player_country_code=player_country_code,
        )


@dataclass
class MarkProofInvalidCommand(Command[None]):
    """Mark an entire proof as invalid"""
    
    time_trial_id: str
    proof_id: str
    validated_by_player_id: int
    version: int

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper) -> None:
        # Input validation
        if not self.proof_id.strip():
            raise Problem("Proof ID is required", status=400)
        if self.validated_by_player_id < 0:
            raise Problem("Validator player ID is required", status=400)
            
        now_iso = datetime.now(timezone.utc).isoformat()

        async with db_wrapper.duckdb.connection() as conn:
            # Find the time trial that contains this proof_id in its embedded proofs
            find_trial_query = """
                SELECT proofs, is_invalid, version 
                FROM time_trials 
                WHERE id = $trial_id
            """
            async with conn.execute(find_trial_query, {"trial_id": self.time_trial_id}) as cursor:
                trial_rows = await cursor.fetchone()
                if not trial_rows:
                    raise Problem(f"Time trial with ID {self.time_trial_id} not found", status=404)
            
            # Parse the JSON string to get the actual proofs data
            proofs_json, is_invalid, current_version = trial_rows
            
            # Check version for optimistic locking
            if current_version != self.version:
                raise Problem(f"Version mismatch. Expected version {self.version}, but current version is {current_version}. Please refresh and try again.", status=409)
            
            if is_invalid:
                raise Problem(f"Time trial {self.time_trial_id} is marked as invalid", status=400)

            proofs_data = msgspec.json.decode(proofs_json, type=List[TimeTrialProof]) if proofs_json else []

            proof_data = None
            for proof in proofs_data:
                if proof.id == self.proof_id:
                    proof_data = proof
                    break
            
            if proof_data is None:
                raise Problem(f"Proof with id {self.proof_id} not found in time trial {self.time_trial_id}", status=404)

            proof_data.status = "invalid"
            proof_data.validator_id = self.validated_by_player_id
            proof_data.validated_at = now_iso

            new_validation_status = calculate_validation_status(proofs_data, record_is_invalid=False)
            new_version = current_version + 1

            update_trial_query = """
                UPDATE time_trials 
                SET proofs = $proofs, validation_status = $validation_status, version = $version, updated_at = $updated_at
                WHERE id = $time_trial_id AND version = $current_version
            """
            await conn.execute(update_trial_query, {
                "proofs": msgspec.json.encode(proofs_data).decode(),
                "validation_status": new_validation_status,
                "version": new_version,
                "updated_at": now_iso,
                "time_trial_id": self.time_trial_id,
                "current_version": current_version
            })


@dataclass
class MarkProofValidCommand(Command[None]):
    """Mark an entire proof as valid (validates both track and time for MVP)."""
    
    time_trial_id: str
    proof_id: str
    validated_by_player_id: int
    version: int

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper) -> None:
        if not self.proof_id.strip():
            raise Problem("Proof ID is required", status=400)
        if self.validated_by_player_id < 0:
            raise Problem("Validator player ID is required", status=400)
            
        now_iso = datetime.now(timezone.utc).isoformat()

        async with db_wrapper.duckdb.connection() as conn:
            # Find the time trial that contains this proof_id in its embedded proofs
            find_trial_query = """
                SELECT proofs, is_invalid, version 
                FROM time_trials 
                WHERE id = $time_trial_id
            """
            async with conn.execute(find_trial_query, {"time_trial_id": self.time_trial_id}) as cursor:
                trial_rows = await cursor.fetchone()
                if not trial_rows:
                    raise Problem(f"Time trial with ID {self.time_trial_id} not found", status=404)
            
            # Parse the JSON string to get the actual proofs data
            proofs_json, is_invalid, current_version = trial_rows
            
            if current_version != self.version:
                raise Problem(f"Version mismatch. Expected version {self.version}, but current version is {current_version}. Please refresh and try again.", status=409)
            
            if is_invalid:
                raise Problem(f"Time trial {self.time_trial_id} is marked as invalid", status=400)

            proofs_data = msgspec.json.decode(proofs_json, type=List[TimeTrialProof]) if proofs_json else []

            proof_data = None
            for proof in proofs_data:
                if proof.id == self.proof_id:
                    proof_data = proof
                    break
            
            if proof_data is None:
                raise Problem(f"Proof with id {self.proof_id} not found in time trial {self.time_trial_id}", status=404)

            proof_data.status = "valid"
            proof_data.validator_id = self.validated_by_player_id
            proof_data.validated_at = now_iso

            new_validation_status = calculate_validation_status(proofs_data, record_is_invalid=False)
            new_version = current_version + 1
            
            # Update the time trial with the modified proofs
            update_trial_query = """
                UPDATE time_trials 
                SET proofs = $proofs, validation_status = $validation_status, version = $version, updated_at = $updated_at
                WHERE id = $time_trial_id AND version = $current_version
            """
            await conn.execute(update_trial_query, {
                "proofs": msgspec.json.encode(proofs_data).decode(),
                "validation_status": new_validation_status,
                "version": new_version,
                "updated_at": now_iso,
                "time_trial_id": self.time_trial_id,
                "current_version": current_version
            })


@dataclass
class ListProofsForValidationCommand(Command[ListProofsForValidationResponseData]):
    """List all proofs with their validation statuses."""
    
    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper) -> ListProofsForValidationResponseData:
        main_sqlite_db_path = db_wrapper.db_paths.get('main')
        if not main_sqlite_db_path:
            raise Problem("Main SQLite database not configured", status=500)

        async with db_wrapper.duckdb.connection() as conn:
            get_all_time_trials_query = f"""
                ATTACH '{main_sqlite_db_path}' AS main_sqlite_db (READ_ONLY, TYPE sqlite);

                SELECT 
                    tt.id, tt.player_id, tt.game, tt.track, tt.time_ms, tt.proofs, tt.version,
                    p.name AS player_name, p.country_code AS player_country_code
                FROM time_trials tt
                LEFT JOIN main_sqlite_db.players p ON tt.player_id = p.id
                WHERE tt.validation_status = 'unvalidated' AND tt.is_invalid = false
                ORDER BY tt.created_at DESC
            """

            async with conn.execute(get_all_time_trials_query) as cursor:
                all_trial_rows = await cursor.fetchall()

        response_proofs: List[ProofWithValidationStatusResponseData] = []
        for trial_row in all_trial_rows:
            tt_id, tt_player_id, tt_game, tt_track, tt_time_ms, tt_proofs_json, tt_version, player_name, player_country_code = trial_row
            
            try:
                # Parse embedded proofs
                proofs_data = msgspec.json.decode(tt_proofs_json, type=List[TimeTrialProof]) if tt_proofs_json else []
            except msgspec.DecodeError:
                # Skip malformed time trial records
                print(f"Error decoding JSON for time_trial_id {tt_id}")
                continue

            # Process each proof in this time trial
            for proof_data in proofs_data:
                p_id = proof_data.id
                if not p_id:
                    continue

                proof_data_obj = ProofRequestData(
                    url=proof_data.url,
                    type=proof_data.type,
                )

                p_created_at = proof_data.created_at
                proof_status = proof_data.status

                # Check if this proof should be excluded from validation queue
                should_include_proof = True
                
                if proof_status in ["valid", "invalid"]:
                    should_include_proof = False
                
                if not should_include_proof:
                    continue

                response_proofs.append(
                    ProofWithValidationStatusResponseData(
                        id=p_id,
                        time_trial_id=tt_id,
                        player_id=tt_player_id,
                        player_name=player_name,
                        player_country_code=player_country_code,
                        game=tt_game,
                        proof_data=proof_data_obj,
                        created_at=p_created_at,
                        track=tt_track,
                        time_ms=tt_time_ms,
                        version=tt_version,
                    )
                )
            
        return ListProofsForValidationResponseData(proofs=response_proofs)


@dataclass
class GetLeaderboardCommand(Command[List[TimeTrialResponseData]]):
    game: str
    track: str
    include_unvalidated: bool = False  # Include records with unvalidated proofs
    include_proofless: bool = False    # Include records without proofs

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper) -> List[TimeTrialResponseData]:
        main_sqlite_db_path = db_wrapper.db_paths.get('main')
        if not main_sqlite_db_path:
            raise Problem("Main SQLite database not configured", status=500)
        
        # Build validation status filter (additive logic)
        validation_filters = ["tt.validation_status = 'valid'"]  # Always include valid
        
        if self.include_unvalidated:
            validation_filters.append("tt.validation_status = 'unvalidated'")
            
        if self.include_proofless:
            validation_filters.append("tt.validation_status = 'proofless'")
        
        # Never include invalid records (tt.validation_status = 'invalid')
        validation_condition = f"({' OR '.join(validation_filters)})"
        
        # Build WHERE conditions
        query_params = { "game": self.game, "track": self.track }
        
        # Simple and efficient query using precomputed validation_status
        query = f"""
            ATTACH '{main_sqlite_db_path}' AS main_sqlite_db (READ_ONLY, TYPE sqlite);

            WITH ranked_times AS (
                SELECT 
                    tt.id, tt.version, tt.player_id, tt.game, tt.track, tt.time_ms,
                    tt.proofs, tt.created_at, tt.updated_at, tt.validation_status,
                    ROW_NUMBER() OVER (
                        PARTITION BY tt.player_id
                        ORDER BY tt.time_ms ASC, tt.created_at ASC
                    ) as rn
                FROM time_trials tt
                WHERE {validation_condition} AND tt.is_invalid = false AND tt.game = $game AND tt.track = $track
            )
            SELECT 
                ranked_times.id, version, player_id, game, track, time_ms,
                proofs, created_at, updated_at, validation_status,
                p.name as player_name, p.country_code
            FROM ranked_times
            LEFT JOIN main_sqlite_db.players p ON ranked_times.player_id = p.id
            WHERE rn = 1
            ORDER BY time_ms ASC, created_at ASC
        """
        
        async with db_wrapper.duckdb.connection() as conn:
            records: List[TimeTrialResponseData] = []
            async with conn.execute(query, query_params) as cursor:
                async for row in cursor:
                    try:
                        id, version, player_id, game, track, time_ms, proofs_str, created_at, updated_at, validation_status, player_name, country_code = row
                        # Parse proofs JSON and filter out invalid ones for response
                        proofs_data = msgspec.json.decode(proofs_str, type=list[TimeTrialProof]) if proofs_str else []
                        proof_responses: list[ProofResponseData] = []
                        for proof in proofs_data:
                            # Only include proofs that are not marked as invalid
                            proof_status = proof.status
                            if proof_status != "invalid":
                                proof_responses.append(ProofResponseData(
                                    id=proof.id,
                                    url=proof.url,
                                    type=proof.type,
                                    created_at=proof.created_at,
                                    status=proof_status,
                                    validator_id=proof.validator_id,
                                    validated_at=proof.validated_at,
                                ))
                        
                        record = TimeTrialResponseData(
                            id=id,
                            version=version,
                            player_id=player_id,
                            game=game,
                            track=track,
                            time_ms=time_ms,
                            proofs=proof_responses,
                            created_at=created_at,
                            updated_at=updated_at,
                            player_name=player_name,
                            player_country_code=country_code,
                            validation_status=validation_status
                        )

                        records.append(record)
                        
                    except Exception as e:
                        print(f"Error processing leaderboard record {row[0]}: {e}")
                        continue
            
            return records


@dataclass
class MarkTimeTrialInvalidCommand(Command[None]):
    """Mark an entire time trial record as invalid by setting is_invalid=true."""
    
    time_trial_id: str
    validated_by_player_id: str
    version: int

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper) -> None:
        # Input validation
        if not self.time_trial_id.strip():
            raise Problem("Time trial ID is required", status=400)
        if not self.validated_by_player_id.strip():
            raise Problem("Validator player ID is required", status=400)
            
        now_iso = datetime.now(timezone.utc).isoformat()

        async with db_wrapper.duckdb.connection() as conn:
            # Check if the time trial exists and get current version
            check_trial_query = """
                SELECT id, is_invalid, version 
                FROM time_trials 
                WHERE id = $time_trial_id
            """
            async with conn.execute(check_trial_query, {"time_trial_id": self.time_trial_id}) as cursor:
                trial_row = await cursor.fetchone()
                if not trial_row:
                    raise Problem(f"Time trial with ID {self.time_trial_id} not found", status=404)
            
            _, _, current_version = trial_row
            
            # Check version for optimistic locking
            if current_version != self.version:
                raise Problem(f"Version mismatch. Expected version {self.version}, but current version is {current_version}. Please refresh and try again.", status=409)
            
            new_version = current_version + 1
            
            # Mark the entire time trial as invalid
            update_query = """
                UPDATE time_trials 
                SET is_invalid = true, validation_status = 'invalid', version = $version, updated_at = $updated_at
                WHERE id = $time_trial_id AND version = $current_version
            """
            await conn.execute(update_query, {
                "version": new_version,
                "updated_at": now_iso,
                "time_trial_id": self.time_trial_id,
                "current_version": current_version
            })


@dataclass
class EditTimeTrialCommand(Command[TimeTrialResponseData]):
    """Edit an existing time trial with comprehensive permission checking."""
    
    time_trial_id: str
    game: str
    track: str
    time_ms: int
    proofs: List[EditProofDictRequired]
    version: int
    current_player_id: int  # ID of logged-in player making the edit
    player_id: int | None
    is_invalid: bool | None
    can_validate: bool = False

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper) -> TimeTrialResponseData:
        if not self.time_trial_id.strip():
            raise Problem("Time trial ID is required", status=400)
        if not self.game.strip():
            raise Problem("Game is required", status=400)
        if not self.track.strip():
            raise Problem("Track is required", status=400)
        if self.time_ms <= 0:
            raise Problem("Time must be positive", status=400)

        now_iso = datetime.now(timezone.utc).isoformat()
        new_version = self.version + 1

        async with db_wrapper.duckdb.connection() as conn:
            # Get current time trial
            get_trial_query = f"""
                SELECT tt.id, tt.version, tt.player_id, tt.game, tt.track, tt.time_ms, 
                       tt.proofs, tt.created_at, tt.updated_at, tt.is_invalid, tt.validation_status
                FROM time_trials tt
                WHERE tt.id = $time_trial_id
            """
            
            async with conn.execute(get_trial_query, {"time_trial_id": self.time_trial_id}) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem(f"Time trial with ID {self.time_trial_id} not found", status=404)
            
            (_, current_version, current_player_id_db, current_game, current_track, 
             current_time_ms, current_proofs_json, created_at, _, current_is_invalid, 
             _) = row

            # Version check
            if current_version != self.version:
                raise Problem(f"Version mismatch. Expected version {self.version}, but current version is {current_version}. Please refresh and try again.", status=409)

            # Permission checks
            is_owner = current_player_id_db == self.current_player_id
            
            # Only owner or validators can edit
            if not is_owner and not self.can_validate:
                raise Problem("You don't have permission to edit this time trial", status=403)

            # Only validators can change player_id
            if self.player_id != current_player_id_db and not self.can_validate:
                raise Problem("Only validators can change the player", status=403)

            # Only validators can modify is_invalid
            if self.is_invalid != current_is_invalid and not self.can_validate:
                raise Problem("Only validators can modify invalid status", status=403)
            
            player_id = self.player_id if self.player_id is not None else int(current_player_id_db)
            is_invalid = self.is_invalid if self.is_invalid is not None else bool(current_is_invalid)

            # Parse current proofs
            current_proofs_data = msgspec.json.decode(current_proofs_json, type=List[TimeTrialProof]) if current_proofs_json else []
            
            # Process proof changes
            updated_proofs = []
            core_fields_changed: bool = (
                self.game != current_game or 
                self.track != current_track or 
                self.time_ms != current_time_ms or
                player_id != current_player_id_db
            )

            for proof_data in self.proofs:
                if proof_data.get('deleted', False):
                    # Check if user can delete this proof
                    proof_id = proof_data.get('id')
                    if proof_id:
                        existing_proof = next((p for p in current_proofs_data if p.id == proof_id), None)
                        if existing_proof:
                            # Only validators can remove validated or invalid proofs
                            if existing_proof.status in ["valid", "invalid"] and not self.can_validate:
                                raise Problem(f"Only validators can remove proofs that have been validated or marked invalid", status=403)
                    
                    # Skip deleted proofs (they won't be included in updated_proofs)
                    continue
                
                proof_id = proof_data.get('id')
                if proof_id:
                    # Editing existing proof
                    existing_proof = next((p for p in current_proofs_data if p.id == proof_id), None)
                    if not existing_proof:
                        raise Problem(f"Proof with ID {proof_id} not found", status=400)
                    
                    # Check if proof content changed
                    proof_changed = (
                        proof_data['url'] != existing_proof.url or
                        proof_data['type'] != existing_proof.type
                    )
                    
                    # Determine new status
                    if core_fields_changed or proof_changed:
                        # Core fields or proof changed - reset to unvalidated
                        new_status = "unvalidated"
                        validator_id = None
                        validated_at = None
                    else:
                        # Check if validator is trying to change status
                        requested_status = proof_data.get('status')
                        if requested_status is not None and requested_status != existing_proof.status:
                            if not self.can_validate:
                                raise Problem("Only validators can modify proof validation status", status=403)
                            new_status = requested_status
                            validator_id = self.current_player_id if requested_status in ["valid", "invalid"] else None
                            validated_at = now_iso if requested_status in ["valid", "invalid"] else None
                        else:
                            # Keep existing status
                            new_status = existing_proof.status
                            validator_id = existing_proof.validator_id
                            validated_at = existing_proof.validated_at
                    
                    updated_proof = TimeTrialProof(
                        id=proof_id,
                        url=proof_data['url'].strip(),
                        type=proof_data['type'].strip(),
                        status=new_status,
                        created_at=existing_proof.created_at,
                        validator_id=validator_id,
                        validated_at=validated_at
                    )
                else:
                    # New proof
                    if not proof_data['url'].strip():
                        raise Problem("Proof URL is required", status=400)
                    if not proof_data['type'].strip():
                        raise Problem("Proof type is required", status=400)
                    
                    # New proofs start as unvalidated unless validator explicitly sets status
                    requested_status = proof_data.get('status') or 'unvalidated'
                    if requested_status != 'unvalidated' and not self.can_validate:
                        raise Problem("Only validators can set initial proof validation status", status=403)
                    
                    updated_proof = TimeTrialProof(
                        id=str(uuid.uuid4()),
                        url=proof_data['url'].strip(),
                        type=proof_data['type'].strip(),
                        status=requested_status,
                        created_at=now_iso,
                        validator_id=self.current_player_id if requested_status in ["valid", "invalid"] else None,
                        validated_at=now_iso if requested_status in ["valid", "invalid"] else None
                    )
                
                updated_proofs.append(updated_proof)

            # Calculate new validation status
            new_validation_status = calculate_validation_status(updated_proofs, is_invalid)
            
            # Update the time trial
            updated_proofs_json = msgspec.json.encode(updated_proofs).decode() if updated_proofs else None
            
            update_query = """
                UPDATE time_trials 
                SET game = $game, track = $track, time_ms = $time_ms, proofs = $proofs,
                    player_id = $player_id, is_invalid = $is_invalid, 
                    validation_status = $validation_status, version = $version, updated_at = $updated_at
                WHERE id = $time_trial_id AND version = $current_version
            """
            
            await conn.execute(update_query, {
                "game": self.game,
                "track": self.track,
                "time_ms": self.time_ms,
                "proofs": updated_proofs_json,
                "player_id": player_id,
                "is_invalid": is_invalid,
                "validation_status": new_validation_status,
                "version": new_version,
                "updated_at": now_iso,
                "time_trial_id": self.time_trial_id,
                "current_version": current_version
            })

            # Return updated data
            response_proofs = [
                ProofResponseData(
                    id=proof.id,
                    url=proof.url,
                    type=proof.type,
                    created_at=proof.created_at,
                    status=proof.status,
                    validator_id=proof.validator_id,
                    validated_at=proof.validated_at
                )
                for proof in updated_proofs
            ]

            return TimeTrialResponseData(
                id=self.time_trial_id,
                version=new_version,
                player_id=player_id,
                game=self.game,
                track=self.track,
                time_ms=self.time_ms,
                proofs=response_proofs,
                created_at=created_at,
                updated_at=now_iso,
                validation_status=new_validation_status,
                player_name=None,
                player_country_code=None
            )

@dataclass
class GetTimesheetCommand(Command[List[TimeTrialResponseData]]):
    """Get all time trials for a specific player and game across all tracks."""
    
    filter: TimesheetFilter

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper) -> List[TimeTrialResponseData]:
        if not self.filter.player_id:
            raise Problem("Player ID is required", status=400)
        if not self.filter.game.strip():
            raise Problem("Game is required", status=400)
        
        async with db_wrapper.connect() as conn:
            player_query = "SELECT name, country_code FROM players WHERE id = :player_id"
            async with conn.execute(player_query, {"player_id": self.filter.player_id}) as cursor:
                player_row = await cursor.fetchone()
                if not player_row:
                    raise Problem(f"Player with ID {self.filter.player_id} not found", status=404)
                
        player_name, player_country_code = player_row

        async with db_wrapper.duckdb.connection() as conn:
            validation_filters = ["tt.validation_status = 'valid'"]  # Always include valid
            
            if self.filter.include_unvalidated:
                validation_filters.append("tt.validation_status = 'unvalidated'")
                
            if self.filter.include_proofless:
                validation_filters.append("tt.validation_status = 'proofless'")
            
            # Never include invalid records (tt.validation_status = 'invalid')
            validation_condition = f"({' OR '.join(validation_filters)})"
            
            # Build the WHERE conditions based on filters
            where_conditions = [
                "tt.player_id = $player_id",
                "tt.game = $game",
                "tt.is_invalid = false",  # Exclude invalid time trials
                validation_condition  # Apply validation status filtering
            ]
            
            # For outdated times logic: if include_outdated is False, we only want the best time per track
            if not self.filter.include_outdated:
                # Use a window function to rank times per track, then filter to only rank 1
                query = f"""
                    WITH ranked_times AS (
                        SELECT tt.id, tt.version, tt.player_id, tt.game, tt.track, tt.time_ms, 
                               tt.proofs, tt.created_at, tt.updated_at, tt.validation_status,
                               ROW_NUMBER() OVER (PARTITION BY tt.track ORDER BY tt.time_ms ASC, tt.created_at ASC) as rank
                        FROM time_trials tt
                        WHERE {' AND '.join(where_conditions)}
                    )
                    SELECT id, version, player_id, game, track, time_ms, proofs, created_at, updated_at, 
                           validation_status
                    FROM ranked_times 
                    WHERE rank = 1
                    ORDER BY track ASC, time_ms ASC
                """
            else:
                # Include all times (outdated and current)
                query = f"""
                    SELECT tt.id, tt.version, tt.player_id, tt.game, tt.track, tt.time_ms, 
                           tt.proofs, tt.created_at, tt.updated_at, tt.validation_status
                    FROM time_trials tt
                    WHERE {' AND '.join(where_conditions)}
                    ORDER BY tt.track ASC, tt.time_ms ASC, tt.created_at DESC
                """

            records = []
            async with conn.execute(query, {
                "player_id": self.filter.player_id,
                "game": self.filter.game
            }) as cursor:
                async for row in cursor:
                    (trial_id, version, player_id, game, track, time_ms, 
                     proofs_json, created_at, updated_at, validation_status) = row

                    # Parse proofs and filter out invalid ones (like leaderboard does)
                    response_proofs = []
                    if proofs_json:
                        try:
                            proofs_data = msgspec.json.decode(proofs_json, type=List[TimeTrialProof])
                            for proof in proofs_data:
                                # Only include proofs that are not marked as invalid
                                if proof.status != "invalid":
                                    response_proofs.append(
                                        ProofResponseData(
                                            id=proof.id,
                                            url=proof.url,
                                            type=proof.type,
                                            created_at=proof.created_at,
                                            status=proof.status,
                                            validator_id=proof.validator_id,
                                            validated_at=proof.validated_at
                                        )
                                    )
                        except Exception:
                            # If proof parsing fails, continue without proofs
                            pass

                    records.append(TimeTrialResponseData(
                        id=trial_id,
                        version=version,
                        player_id=player_id,
                        game=game,
                        track=track,
                        time_ms=time_ms,
                        proofs=response_proofs,
                        created_at=created_at,
                        updated_at=updated_at,
                        validation_status=validation_status,
                        player_name=player_name,
                        player_country_code=player_country_code
                    ))

            return records
