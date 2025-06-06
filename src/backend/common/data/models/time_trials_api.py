"""
Time trials API request and response models.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from common.data.models.time_trials import TimeTrialData


@dataclass
class CreateTimeTrialRequestData:
    """Request data for creating a new time trial."""
    game: str
    track: str
    time_ms: int
    data: Dict[str, Any]  # Will be validated and converted to TimeTrialData
    proof_url: Optional[str] = None
    description: Optional[str] = None


@dataclass 
class TimeTrialResponseData:
    """Response data for time trial records."""
    id: str
    version: int
    player_id: str
    game: str
    track: str
    time_ms: int
    data: TimeTrialData
    proof_url: str
    description: str
    created_at: str
    updated_at: str


@dataclass
class ListTimeTrialsRequestData:
    """Request data for listing time trials with optional filters."""
    player_id: Optional[str] = None
    game: Optional[str] = None
    track: Optional[str] = None
    cc: Optional[int] = None  # Engine class for games that support it (e.g., MK8DX)
    limit: Optional[int] = None
    offset: Optional[int] = None
