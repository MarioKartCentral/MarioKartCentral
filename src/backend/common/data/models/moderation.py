from dataclasses import dataclass, field
from common.data.models.player_basic import PlayerBasic
from typing import Literal

@dataclass
class FilteredWords:
    words: list[str]

@dataclass
class IPInfoBasic:
    user_id: int
    ip_address: str

@dataclass
class IPCheckResponse:
    status: Literal["success", "fail"]
    message: str | None = None
    mobile: bool = False
    proxy: bool = False
    countryCode: str | None = None
    region: str | None = None
    city: str | None = None
    asn: str | None = field(metadata={"alias": "as"}, default=None)

@dataclass
class AltFlagFilter:
    type: str | None = None
    exclude_fingerprints: bool = False
    page: int | None = None

@dataclass
class PlayerAltFlagRequestData:
    player_id: int
    exclude_fingerprints: bool = False

@dataclass
class AltFlagUser:
    user_id: int
    player: PlayerBasic | None

@dataclass
class AltFlag:
    id: int
    type: str
    flag_key: str
    data: str
    score: int
    date: int
    fingerprint_hash: str | None
    users: list[AltFlagUser]

@dataclass
class AltFlagList:
    flags: list[AltFlag]
    count: int
    page_count: int

@dataclass
class IPAddress:
    id: int
    ip_address: str | None # can be null if user doesnt have permissions
    is_mobile: bool
    is_vpn: bool
    country: str | None
    city: str | None
    region: str | None
    asn: str | None

@dataclass
class IPAddressWithUserCount(IPAddress):
    user_count: int

@dataclass
class IPAddressList:
    ip_addresses: list[IPAddressWithUserCount]
    count: int
    page_count: int

@dataclass
class UserLogin:
    id: int
    user_id: int
    fingerprint: str
    had_persistent_session: bool
    date: int
    logout_date: int | None
    ip_address: IPAddress

@dataclass
class PlayerUserLogins:
    player_id: int
    logins: list[UserLogin]

@dataclass
class UserIPTimeRange:
    id: int
    user_id: int
    ip_address: IPAddress
    date_earliest: int
    date_latest: int
    times: int

@dataclass
class PlayerIPHistory:
    player_id: int
    ips: list[UserIPTimeRange]

@dataclass
class PlayerIPTimeRange:
    time_range: UserIPTimeRange
    player: PlayerBasic | None

@dataclass
class IPHistory:
    ip_id: int
    history: list[PlayerIPTimeRange]

@dataclass
class IPFilter:
    ip_address: str | None = None
    city: str | None = None
    asn: str | None = None
    page: int | None = None