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

@dataclass
class ForgotPasswordRequestData:
    email: str

@dataclass
class SendPlayerPasswordResetRequestData:
    player_id: int

@dataclass
class CheckPasswordTokenRequestData:
    token_id: str

@dataclass
class ResetPasswordTokenRequestData:
    token_id: str
    new_password: str

@dataclass
class ResetPasswordRequestData:
    old_password: str
    new_password: str

@dataclass
class TransferAccountRequestData:
    player_id: int

@dataclass
class RemovePlayerAvatarRequestData:
    player_id: int

@dataclass
class ChangeEmailRequestData:
    new_email: str
    password: str

@dataclass
class CreateAPITokenRequestData:
    name: str

@dataclass
class APIToken:
    user_id: int
    token_id: str
    name: str

@dataclass
class DeleteAPITokenRequestData:
    token_id: str