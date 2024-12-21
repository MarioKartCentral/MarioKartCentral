from dataclasses import dataclass
from datetime import timedelta

@dataclass
class SessionInfo:
    session_id: str
    persistent_session_id: str
    max_age: timedelta