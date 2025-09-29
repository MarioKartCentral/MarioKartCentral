from dataclasses import dataclass
from common.data.models.common import CountryCode


@dataclass
class PlayerBasic:
    id: int
    name: str
    country_code: CountryCode
    is_banned: bool