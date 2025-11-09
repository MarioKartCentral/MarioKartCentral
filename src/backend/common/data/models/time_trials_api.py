"""
Time trials API request and response models.
"""

from dataclasses import dataclass
from typing import TypedDict


class EditProofDict(TypedDict, total=False):
    """Type definition for proof data dictionaries in edit operations."""
    id: str | None  # None for new proofs
    deleted: bool
    status: str | None  # Only included when staff sets validation status


class EditProofDictRequired(EditProofDict, total=True):
    """Required fields for proof data dictionaries."""
    url: str
    type: str


@dataclass
class ProofRequestData:
    """Request data for submitting proof evidence."""
    url: str
    type: str


@dataclass
class CreateTimeTrialRequestData:
    """Request data for creating a new time trial."""
    game: str
    track: str
    time_ms: int
    proofs: list[ProofRequestData]
    player_id: int | None = None


@dataclass
class ProofResponseData:
    id: str
    url: str
    type: str
    created_at: str
    status: str | None = "unvalidated"
    validator_id: int | None = None
    validated_at: str | None = None


@dataclass
class TimeTrialResponseData:
    """Response data for time trial records."""
    id: str
    version: int
    player_id: int
    game: str
    track: str
    time_ms: int
    proofs: list[ProofResponseData]
    created_at: str
    updated_at: str
    validation_status: str = "proofless"
    player_name: str | None = None
    player_country_code: str | None = None


@dataclass
class ProofWithValidationStatusResponseData:
    """Proof data with validation status information for validation listing."""
    id: str
    time_trial_id: str
    player_id: str
    game: str
    proof_data: ProofRequestData
    created_at: str
    track: str 
    time_ms: int
    version: int
    player_name: str | None = None
    player_country_code: str | None = None


@dataclass
class ListProofsForValidationResponseData:
    """Response data for listing proofs with their validation statuses."""
    proofs: list[ProofWithValidationStatusResponseData]


@dataclass
class LeaderboardFilter:
    """Filter parameters for leaderboard queries."""
    game: str
    track: str
    include_unvalidated: bool = False
    include_proofless: bool = False

@dataclass
class LeaderboardResponseData:
    """Response data for leaderboard queries."""
    records: list[TimeTrialResponseData]


@dataclass
class MarkProofInvalidRequestData:
    """Request data for marking a proof as invalid."""
    version: int


@dataclass
class MarkProofValidRequestData:
    """Request data for marking a proof as valid."""
    version: int


@dataclass
class MarkTimeTrialInvalidRequestData:
    """Request data for marking a time trial as invalid."""
    version: int


@dataclass
class EditProofData:
    """Data for editing a proof within a time trial."""
    id: str | None = None  # None for new proofs
    url: str = ""
    type: str = ""
    status: str | None = None  # Only editable by validators
    deleted: bool = False  # Mark for deletion


@dataclass
class EditTimeTrialRequestData:
    """Request data for editing an existing time trial."""
    game: str
    track: str
    time_ms: int
    proofs: list[EditProofData]
    version: int
    player_id: int | None = None  # Only editable by validators
    is_invalid: bool | None = None  # Only editable by validators


@dataclass
class TimesheetFilter:
    """Filter parameters for timesheet queries."""
    player_id: int
    game: str
    include_unvalidated: bool = False
    include_proofless: bool = False
    include_outdated: bool = False  # Show older submissions that have been beaten


@dataclass
class TimesheetResponseData:
    """Response data for timesheet queries."""
    records: list[TimeTrialResponseData]