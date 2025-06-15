"""
Time trials API request and response models.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from common.data.models import Problem


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


@dataclass
class TimeTrialFilter:
    """Filter parameters for listing time trials."""
    player_id: Optional[str] = None
    game: Optional[str] = None
    track: Optional[str] = None
    page: int = 1
    page_size: int = 20
    leaderboard_mode: bool = False  # Show only best time per player
    show_unvalidated: bool = False  # Include unvalidated times
    show_without_proof: bool = False  # Include times without proof
    
    def validate(self):
        """Validate filter parameters following established patterns."""
        if self.page < 1:
            raise Problem("Page must be positive", status=400)
        if self.page_size < 1 or self.page_size > 100:
            raise Problem("Page size must be between 1 and 100", status=400)


@dataclass
class ProofResponseData:
    """Response data for proof evidence."""
    id: str
    url: str
    type: str
    created_at: str
    status: Optional[str] = "unvalidated"  # MVP: simplified validation status
    validator_id: Optional[str] = None  # Staff member who validated 
    validated_at: Optional[str] = None  # When validation occurred


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
    player_name: Optional[str] = None
    player_country_code: Optional[str] = None


@dataclass
class ProofWithValidationStatusResponseData:
    """Proof data with validation status information for validation listing."""
    id: str
    time_trial_id: str
    player_id: str
    game: str
    proof_data: Dict[str, Any]
    properties: List[str]  # MVP: Empty list for simplified validation
    created_at: str
    player_name: Optional[str] = None
    player_country_code: Optional[str] = None
    # Time trial data for displaying values to verify
    track: Optional[str] = None
    time_ms: Optional[int] = None


@dataclass  
class ProofWithValidationData:
    """Proof data with validation status information - simplified for MVP."""
    proof: ProofResponseData
    # MVP: No property-specific validation statuses needed


@dataclass
class TimeTrialPropertyValidationData:
    """Validation data for a single time trial property."""
    property_name: str
    current_value: Any  # The current value in the database
    is_validated: bool  # Whether this property has been validated by the proof
    is_correct: bool = True  # Whether the current value is correct


@dataclass
class PropertyValidationData:
    """Individual property validation data."""
    property_name: str
    is_valid: bool
    id: str
    time_trial_id: str
    player_id: str
    game: str
    proof_data: Dict[str, Any]  # URL, type, etc.
    created_at: str
    # Complete time trial data for validation/editing
    time_trial: Dict[str, Any]  # All time trial fields including time_ms, track, data, etc.
    # MVP: Simplified validation - no property-specific tracking
    claimed_properties: List[str] = field(default_factory=list)  # Always empty for MVP


@dataclass
class ListProofsForValidationResponseData:
    """Response data for listing proofs with their validation statuses."""
    proofs: List[ProofWithValidationStatusResponseData]


@dataclass
class EditTimeTrialRequestData:
    """Request data for editing a time trial's properties."""
    track: Optional[str] = None
    time_ms: Optional[int] = None


@dataclass
class PlayerRecordFilter:
    """Filter parameters for listing player records."""
    player_id: Optional[str] = None  # Will be set from path parameter
    game: Optional[str] = None
    track: Optional[str] = None
    show_superseded: bool = False  # Whether to include superseded records
    sort_by: str = "created_at"  # Options: "created_at", "track", "time_ms"
    sort_order: str = "desc"  # Options: "asc", "desc"
    page: int = 1
    page_size: int = 20

    def validate(self):
        """Validate filter parameters."""
        if self.page < 1:
            raise Problem("Page must be positive", status=400)
        if self.page_size < 1 or self.page_size > 100:
            raise Problem("Page size must be between 1 and 100", status=400)
        if self.sort_by not in ["created_at", "track", "time_ms", "updated_at"]:
            raise Problem("Invalid sort_by parameter", status=400)
        if self.sort_order not in ["asc", "desc"]:
            raise Problem("Invalid sort_order parameter", status=400)


@dataclass
class PlayerRecordResponseData:
    """Response data for a player's time trial record."""
    id: str
    version: int
    player_id: str  # Added player ID
    game: str
    track: str
    time_ms: int
    proofs: List[ProofResponseData]
    created_at: str
    updated_at: str
    player_name: Optional[str] = None  # Added player name from players table
    country_code: Optional[str] = None  # Added country code for flag display
    is_superseded: bool = False  # Whether this record has been superseded by a better time
    superseded_by: Optional[str] = None  # ID of the record that superseded this one
    is_current_best: bool = True  # Whether this is the player's current best for this track
    validation_status: str = "proofless"  # Options: "proofless", "unvalidated", "validated", "invalid"


@dataclass
class LeaderboardFilter:
    """Filter parameters for leaderboard queries."""
    game: Optional[str] = None
    track: Optional[str] = None
    include_unvalidated: bool = False  # Include records with unvalidated proofs
    include_proofless: bool = False    # Include records without proofs
    page: int = 1
    page_size: int = 20

    def validate(self):
        """Validate filter parameters."""
        if self.page < 1:
            raise Problem("Page must be positive", status=400)
        if self.page_size < 1 or self.page_size > 100:
            raise Problem("Page size must be between 1 and 100", status=400)


@dataclass  
class ListPlayerRecordsResponseData:
    """Response data for listing a player's records."""
    records: List[PlayerRecordResponseData]
    total_count: int
    page: int
    page_size: int
    has_next_page: bool
