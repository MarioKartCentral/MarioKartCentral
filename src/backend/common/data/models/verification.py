from dataclasses import dataclass
from typing import Literal
from common.data.models.player_basic import PlayerBasic
from common.data.models.friend_codes import FriendCode
from common.data.models.common import CountryCode

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
class PlayerVerificationRequestBasic:
    id: int
    player_id: int
    date: int
    approval_status: VerificationApproval

@dataclass
class FriendCodeVerificationRequestBasic:
    id: int
    fc_id: int
    date: int
    approval_status: VerificationApproval

@dataclass
class CheckPlayerVerificationRequest:
    update_data: UpdatePlayerVerification
    request: PlayerVerificationRequestBasic | None

@dataclass
class CheckFriendCodeVerificationRequest:
    update_data: UpdateFriendCodeVerification
    request: FriendCodeVerificationRequestBasic | None

@dataclass
class PlayerVerificationFilter:
    approval_status: VerificationApproval | None = None
    player_id: int | None = None
    country_code: CountryCode | None = None
    country_code_exclude: CountryCode | None = None
    handled_by: int | None = None
    from_date: int | None = None
    to_date: int | None = None
    get_pending_fc_verifications: bool = False
    page: int | None = None

@dataclass
class VerificationLogItemBasic:
    id: int
    verification_id: int
    date: int
    approval_status: VerificationApproval
    reason: str | None
    handled_by: PlayerBasic

@dataclass
class FriendCodeVerificationRequest:
    id: int
    date: int
    approval_status: VerificationApproval
    player: PlayerBasic
    fc: FriendCode

@dataclass
class PlayerVerificationRequest:
    id: int
    date: int
    approval_status: VerificationApproval
    player: PlayerBasic

@dataclass
class FriendCodeVerificationRequestDetailed(FriendCodeVerificationRequest):
    audit_log: list[VerificationLogItemBasic]

@dataclass
class PlayerVerificationRequestDetailed(PlayerVerificationRequest):
    fc_verifications: list[FriendCodeVerificationRequest]
    audit_log: list[VerificationLogItemBasic]
    alt_flag_count: int = 0

@dataclass
class PlayerVerificationList:
    verifications: list[PlayerVerificationRequestDetailed]
    count: int
    page_count: int

@dataclass
class UpdateVerificationsRequestData:
    player_verifications: list[UpdatePlayerVerification]
    fc_verifications: list[UpdateFriendCodeVerification]