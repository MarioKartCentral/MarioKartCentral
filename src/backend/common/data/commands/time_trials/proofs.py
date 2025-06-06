"""
Proof and validation management commands for time trial verification.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import msgspec

from common.data.commands import Command, save_to_command_log
from common.data.models import Problem
from common.data.duckdb.models import Proof, ProofValidation


@save_to_command_log
@dataclass
class CreateProofCommand(Command[Proof]):
    """Submit proof evidence for a time trial."""
    
    time_trial_id: str
    properties: List[str]  # List of property names this proof validates (e.g., ['character', 'vehicle'])
    proof_data: Dict[str, Any]  # URL, metadata, etc.

    async def handle(self, db_wrapper, s3_wrapper) -> Proof:
        if not self.time_trial_id.strip():
            raise Problem("Time trial ID is required", status=400)
            
        if not self.properties:
            raise Problem("At least one property must be specified", status=400)
            
        if not self.proof_data:
            raise Problem("Proof data is required", status=400)

        # Verify the time trial exists
        async with db_wrapper.duckdb.connection() as conn:
            check_trial_query = "SELECT id FROM time_trials WHERE id = $trial_id"
            async with conn.execute(check_trial_query, {"trial_id": self.time_trial_id}) as cursor:
                if not await cursor.fetchone():
                    raise Problem("Time trial not found", status=404)

        proof = Proof(
            time_trial_id=self.time_trial_id,
            properties=self.properties,
            proof_data=self.proof_data
        )

        async with db_wrapper.duckdb.connection() as conn:
            insert_proof_query = """
                INSERT INTO proofs (id, time_trial_id, properties, proof_data, created_at)
                VALUES ($id, $time_trial_id, $properties, $proof_data, $created_at)
            """
            await conn.execute(insert_proof_query, {
                "id": proof.id,
                "time_trial_id": proof.time_trial_id,
                "properties": msgspec.json.encode(proof.properties).decode(),
                "proof_data": msgspec.json.encode(proof.proof_data).decode(),
                "created_at": proof.created_at,
            })

        return proof


@dataclass
class GetProofCommand(Command[Optional[Proof]]):
    """Retrieve a specific proof by ID."""
    
    proof_id: str

    async def handle(self, db_wrapper, s3_wrapper) -> Optional[Proof]:
        if not self.proof_id.strip():
            raise Problem("Proof ID is required", status=400)

        async with db_wrapper.duckdb.connection() as conn:
            get_proof_query = """
                SELECT id, time_trial_id, properties, proof_data, created_at 
                FROM proofs WHERE id = $proof_id
            """
            async with conn.execute(get_proof_query, {"proof_id": self.proof_id}) as cursor:
                row = await cursor.fetchone()
                if row:
                    id, time_trial_id, properties, proof_data, created_at = row
                    return Proof(
                        id=id,
                        time_trial_id=time_trial_id,
                        properties=msgspec.json.decode(properties.encode(), type=list),
                        proof_data=msgspec.json.decode(proof_data.encode(), type=dict),
                        created_at=created_at
                    )
        return None


@dataclass
class ListProofsByTimeTrialCommand(Command[List[Proof]]):
    """Get all proofs for a specific time trial."""
    
    time_trial_id: str

    async def handle(self, db_wrapper, s3_wrapper) -> List[Proof]:
        if not self.time_trial_id.strip():
            raise Problem("Time trial ID is required", status=400)

        async with db_wrapper.duckdb.connection() as conn:
            list_proofs_query = """
                SELECT id, time_trial_id, properties, proof_data, created_at 
                FROM proofs 
                WHERE time_trial_id = $time_trial_id 
                ORDER BY created_at DESC
            """
            async with conn.execute(list_proofs_query, {"time_trial_id": self.time_trial_id}) as cursor:
                rows = await cursor.fetchall()
                result = []
                for row in rows:
                    id, time_trial_id, properties, proof_data, created_at = row
                    result.append(Proof(
                        id=id,
                        time_trial_id=time_trial_id,
                        properties=msgspec.json.decode(properties.encode(), type=list),
                        proof_data=msgspec.json.decode(proof_data.encode(), type=dict),
                        created_at=created_at
                    ))
                return result


@save_to_command_log
@dataclass
class CreateProofValidationCommand(Command[ProofValidation]):
    """Staff validation of submitted proof."""
    
    proof_id: str
    staff_id: str
    is_valid: bool
    notes: str = ""

    async def handle(self, db_wrapper, s3_wrapper) -> ProofValidation:
        if not self.proof_id.strip():
            raise Problem("Proof ID is required", status=400)
            
        if not self.staff_id.strip():
            raise Problem("Staff ID is required", status=400)

        # Verify the proof exists
        async with db_wrapper.duckdb.connection() as conn:
            check_proof_query = "SELECT id FROM proofs WHERE id = $proof_id"
            async with conn.execute(check_proof_query, {"proof_id": self.proof_id}) as cursor:
                if not await cursor.fetchone():
                    raise Problem("Proof not found", status=404)

        validation = ProofValidation(
            proof_id=self.proof_id,
            staff_id=self.staff_id,
            is_valid=self.is_valid,
            notes=self.notes
        )

        async with db_wrapper.duckdb.connection() as conn:
            insert_validation_query = """
                INSERT INTO proof_validations (id, proof_id, staff_id, is_valid, validated_at, notes)
                VALUES ($id, $proof_id, $staff_id, $is_valid, $validated_at, $notes)
            """
            await conn.execute(insert_validation_query, {
                "id": validation.id,
                "proof_id": validation.proof_id,
                "staff_id": validation.staff_id,
                "is_valid": validation.is_valid,
                "validated_at": validation.validated_at,
                "notes": validation.notes,
            })

        return validation


@dataclass
class GetProofValidationsCommand(Command[List[ProofValidation]]):
    """Get all validations for a specific proof."""
    
    proof_id: str

    async def handle(self, db_wrapper, s3_wrapper) -> List[ProofValidation]:
        if not self.proof_id.strip():
            raise Problem("Proof ID is required", status=400)

        async with db_wrapper.duckdb.connection() as conn:
            get_validations_query = """
                SELECT id, proof_id, staff_id, is_valid, validated_at, notes 
                FROM proof_validations 
                WHERE proof_id = $proof_id 
                ORDER BY validated_at DESC
            """
            async with conn.execute(get_validations_query, {"proof_id": self.proof_id}) as cursor:
                rows = await cursor.fetchall()
                result = []
                for row in rows:
                    id, proof_id, staff_id, is_valid, validated_at, notes = row
                    result.append(ProofValidation(
                        id=id,
                        proof_id=proof_id,
                        staff_id=staff_id,
                        is_valid=bool(is_valid),
                        validated_at=validated_at,
                        notes=notes
                    ))
                return result


@dataclass
class GetValidationsByStaffCommand(Command[List[ProofValidation]]):
    """Get all validations performed by a specific staff member."""
    
    staff_id: str
    limit: int = 100

    async def handle(self, db_wrapper, s3_wrapper) -> List[ProofValidation]:
        if not self.staff_id.strip():
            raise Problem("Staff ID is required", status=400)
            
        if self.limit <= 0 or self.limit > 1000:
            raise Problem("Limit must be between 1 and 1000", status=400)

        async with db_wrapper.duckdb.connection() as conn:
            get_staff_validations_query = """
                SELECT id, proof_id, staff_id, is_valid, validated_at, notes 
                FROM proof_validations 
                WHERE staff_id = $staff_id 
                ORDER BY validated_at DESC 
                LIMIT $limit
            """
            async with conn.execute(get_staff_validations_query, {"staff_id": self.staff_id, "limit": self.limit}) as cursor:
                rows = await cursor.fetchall()
                result = []
                for row in rows:
                    id, proof_id, staff_id, is_valid, validated_at, notes = row
                    result.append(ProofValidation(
                        id=id,
                        proof_id=proof_id,
                        staff_id=staff_id,
                        is_valid=bool(is_valid),
                        validated_at=validated_at,
                        notes=notes
                    ))
                return result
