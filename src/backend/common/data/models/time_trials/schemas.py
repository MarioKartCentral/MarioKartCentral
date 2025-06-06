"""
Game-specific data schemas for time trial data field.

These schemas define the structure of the `data` field in time trials
based on the game being played. They provide type safety and validation
for game-specific properties.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import msgspec


@dataclass
class TimeTrialData:
    """Base schema for time trial data field."""
    
    # Common properties across all games (all optional)
    lap_times: Optional[List[int]] = None  # Individual lap times in milliseconds
    character: Optional[str] = None  # Character used for the time trial
    kart: Optional[str] = None  # Kart/vehicle used for the time trial


@dataclass  
class MK8DXTimeTrialData(TimeTrialData):
    """Mario Kart 8 Deluxe specific time trial data."""
    
    # MK8DX specific properties (all optional)
    tires: Optional[str] = None  # Tire selection
    glider: Optional[str] = None  # Glider selection
    cc: Optional[int] = None  # Engine class (150 or 200)


@dataclass
class MKWorldTimeTrialData(TimeTrialData):
    """Mario Kart World specific time trial data."""
    
    # MKWorld specific properties (none defined yet, but ready for future expansion)
    pass


# Game identifier to schema mapping
GAME_SCHEMAS = {
    "mk8dx": MK8DXTimeTrialData,
    "mkworld": MKWorldTimeTrialData,
}


def get_schema_for_game(game: str) -> type[TimeTrialData]:
    """Get the appropriate schema class for a given game identifier."""
    return GAME_SCHEMAS.get(game.lower(), TimeTrialData)


def deserialize_time_trial_data_from_json(json_str: str, game: str) -> TimeTrialData:
    """Deserialize time trial data directly from JSON string using the appropriate game schema."""
    schema_class = get_schema_for_game(game)
    return msgspec.json.decode(json_str.encode(), type=schema_class)


def validate_and_create_time_trial_data(data: Dict[str, Any], game: str) -> TimeTrialData:
    """Validate incoming data and create the appropriate schema object.
    
    This is useful for API endpoints that receive JSON data and need to validate
    it against the appropriate game schema before storing it.
    
    Args:
        data: Raw dictionary data from API request
        game: Game identifier to determine which schema to use
        
    Returns:
        Validated and typed data object
        
    Raises:
        ValueError: If data doesn't match the expected schema
    """
    try:
        return deserialize_time_trial_data(data, game)
    except Exception as e:
        schema_class = get_schema_for_game(game)
        raise ValueError(f"Invalid data for game '{game}'. Expected schema: {schema_class.__name__}. Error: {e}")


def deserialize_time_trial_data(data: Dict[str, Any], game: str) -> TimeTrialData:
    """Deserialize time trial data using the appropriate game schema."""
    schema_class = get_schema_for_game(game)
    return msgspec.convert(data, type=schema_class)


def serialize_time_trial_data(data: TimeTrialData) -> Dict[str, Any]:
    """Serialize time trial data to a dictionary."""
    return msgspec.to_builtins(data)
