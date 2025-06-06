"""
Time trials models and schemas.
"""

from .schemas import (
    TimeTrialData,
    MK8DXTimeTrialData,
    MKWorldTimeTrialData,
    get_schema_for_game,
    deserialize_time_trial_data,
    deserialize_time_trial_data_from_json,
    serialize_time_trial_data,
    validate_and_create_time_trial_data,
)

__all__ = [
    "TimeTrialData",
    "MK8DXTimeTrialData", 
    "MKWorldTimeTrialData",
    "get_schema_for_game",
    "deserialize_time_trial_data",
    "deserialize_time_trial_data_from_json",
    "serialize_time_trial_data",
    "validate_and_create_time_trial_data",
]
