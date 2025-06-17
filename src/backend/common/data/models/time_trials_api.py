"""
Time trials API request and response models.
"""

from dataclasses import dataclass
from typing import Optional, List, TypedDict


class EditProofDict(TypedDict, total=False):
    """Type definition for proof data dictionaries in edit operations."""
    id: Optional[str]  # None for new proofs
    deleted: bool
    status: Optional[str]  # Only included when staff sets validation status


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
    proofs: List[ProofRequestData]
    player_id: Optional[int] = None


@dataclass
class ProofResponseData:
    id: str
    url: str
    type: str
    created_at: str
    status: Optional[str] = "unvalidated"
    validator_id: Optional[int] = None
    validated_at: Optional[str] = None


@dataclass
class TimeTrialResponseData:
    """Response data for time trial records."""
    id: str
    version: int
    player_id: int
    game: str
    track: str
    time_ms: int
    proofs: List[ProofResponseData]
    created_at: str
    updated_at: str
    validation_status: str = "proofless"
    player_name: Optional[str] = None
    player_country_code: Optional[str] = None
    can_edit: bool = False


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
    player_name: Optional[str] = None
    player_country_code: Optional[str] = None


@dataclass
class ListProofsForValidationResponseData:
    """Response data for listing proofs with their validation statuses."""
    proofs: List[ProofWithValidationStatusResponseData]


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
    records: List[TimeTrialResponseData]


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
    id: Optional[str] = None  # None for new proofs
    url: str = ""
    type: str = ""
    status: Optional[str] = None  # Only editable by validators
    deleted: bool = False  # Mark for deletion


@dataclass
class EditTimeTrialRequestData:
    """Request data for editing an existing time trial."""
    game: str
    track: str
    time_ms: int
    proofs: List[EditProofData]
    version: int
    player_id: Optional[int] = None  # Only editable by validators
    is_invalid: Optional[bool] = None  # Only editable by validators


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
    records: List[TimeTrialResponseData]