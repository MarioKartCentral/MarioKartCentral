from dataclasses import dataclass
from typing import Literal

VerificationApproval = Literal["approved", "pending", "ticket", "denied"]

@dataclass
class RequestVerificationRequestData:
    verify_player: bool
    friend_code_ids: list[int]

@dataclass
class UpdatePlayerVerification:
    verification_id: int
    approval_status: VerificationApproval
    reason: str | None

@dataclass
class UpdateFriendCodeVerification:
    verification_id: int
    approval_status: VerificationApproval
    reason: str | None

@dataclass
class PlayerVerificationRequest:
    id: int
    player_id: int
    date: int
    approval_status: VerificationApproval

@dataclass
class FriendCodeVerificationRequest:
    id: int
    fc_id: int
    date: int
    approval_status: VerificationApproval

@dataclass
class CheckPlayerVerificationRequest:
    update_data: UpdatePlayerVerification
    request: PlayerVerificationRequest | None

@dataclass
class CheckFriendCodeVerificationRequest:
    update_data: UpdateFriendCodeVerification
    request: FriendCodeVerificationRequest | None