from dataclasses import dataclass
from common.config.common import load_config

@dataclass
class CompetitiveDataGame:
    modes: list[str]

@dataclass
class CompetitiveData:
    games: dict[str, CompetitiveDataGame]

competitive_config = load_config("competitive.json", CompetitiveData)