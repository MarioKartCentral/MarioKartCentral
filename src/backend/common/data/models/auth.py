from dataclasses import dataclass
from typing import Any
from datetime import timedelta

@dataclass
class Fingerprint:
    hash: str
    data: dict[Any, Any]

@dataclass
class LoginRequestData:
    email: str
    password: str
    fingerprint: Fingerprint

@dataclass
class SignupRequestData:
    email: str
    password: str
    fingerprint: Fingerprint

@dataclass
class SessionInfo:
    session_id: str
    persistent_session_id: str
    max_age: timedelta

@dataclass
class ConfirmEmailRequestData:
    token_id: str