from dataclasses import dataclass
from typing import Any, Literal


@dataclass
class Problem(Exception):
    """
    A schema for describing an error, based on RFC-7807: https://www.rfc-editor.org/rfc/rfc7807

    title:
        A short, human-readable explanation of the error.
        The title should have the same value for all instances of this error.

    detail:
        An optional, more detailed human-readable explanation of the error.
        Additional information specific to this instance of the error can be included.

    data:
        An optional bag of additional data to go with the error
    """

    title: str
    detail: str | None = None
    status: int = 500
    data: dict[str, Any] | None = None

    def __str__(self) -> str:
        s = f"{self.title} (HTTP {self.status})"
        if self.detail:
            s += f"\n{self.detail}"
        if self.data:
            for k, v in self.data.items():
                s += f"\n{k}: {v}"
        return s


Game = Literal["mkw", "mk7", "mk8", "mk8dx", "mkt", "smk"]
GameMode = Literal[
    "150cc",
    "200cc",
    "rt",
    "ct",
    "vsrace",
    "match_race",
    "mixed_battle",
    "balloon_battle",
    "shine_thief",
    "bobomb_blast",
    "coin_runners",
    "renegade_roundup",
    "mixed",
]
FriendCodeType = Literal["switch", "nnid", "3ds", "mkw", "mkt"]
game_fc_map: dict[Game, FriendCodeType] = {
                    "mk8dx": "switch",
                    "mk7": "3ds",
                    "mk8": "nnid",
                    "mkt": "mkt",
                    "mkw": "mkw",
                    "smk": "switch"
                }
Approval = Literal["approved", "pending", "denied"]
CountryCode = Literal["AF", "AX", "AL", "DZ", "AS", "AD", "AO", "AI", "AQ", "AG", "AR", "AM", "AW", "AU", "AT", "AZ", "BS",
                      "BH", "BD", "BB", "BY", "BE", "BZ", "BJ", "BM", "BT", "BO", "BQ", "BA", "BW", "BV", "BR", "IO", "BN",
                      "BG", "BF", "BI", "CV", "KH", "CM", "CA", "KY", "CF", "TD", "CL", "CN", "CX", "CC", "CO", "KM", "CD",
                      "CG", "CK", "CR", "CI", "HR", "CU", "CW", "CY", "CZ", "DK", "DJ", "DM", "DO", "EC", "EG", "SV", "GQ",
                      "ER", "EE", "SZ", "ET", "FK", "FO", "FJ", "FI", "FR", "GF", "PF", "TF", "GA", "GM", "GE", "DE", "GH",
                      "GI", "GR", "GL", "GD", "GP", "GU", "GT", "GG", "GN", "GW", "GY", "GT", "HM", "VA", "HN", "HK", "HU",
                      "IS", "IN", "ID", "IR", "IQ", "IE", "IM", "IL", "IT", "JM", "JP", "JE", "JO", "KZ", "KE", "KI", "KP",
                      "KR", "KW", "KG", "LA", "LV", "LB", "LS", "LR", "LY", "LI", "LT", "LU", "MO", "MK", "MG", "MW", "MY",
                      "MV", "ML", "MT", "MH", "MQ", "MR", "MU", "YT", "MX", "FM", "MD", "MC", "MN", "ME", "MS", "MA", "MZ",
                      "MM", "NA", "NR", "NP", "NL", "NC", "NZ", "NI", "NE", "NG", "NU", "NF", "MP", "NO", "OM", "PK", "PW",
                      "PS", "PA", "PG", "PY", "PE", "PH", "PN", "PL", "PT", "PR", "QA", "RE", "RO", "RU", "RW", "BL", "SH",
                      "KN", "LC", "MF", "PM", "VC", "WS", "SM", "ST", "SA", "SN", "RS", "SC", "SL", "SG", "SX", "SI", "SB",
                      "SO", "ZA", "GS", "SS", "ES", "LK", "SD", "SR", "SJ", "SE", "CH", "SY", "TW", "TJ", "TZ", "TH", "TL",
                      "TG", "TK", "TO", "TT", "TN", "TR", "TM", "TC", "TV", "UG", "UA", "AE", "GB", "UM", "US", "UY", "UZ",
                      "VU", "VE", "VN", "VG", "VI", "WF", "EH", "YE", "ZM", "ZW"]
