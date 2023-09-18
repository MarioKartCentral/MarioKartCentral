from dataclasses import dataclass
from common.config.common import load_config

@dataclass
class CompetitiveDataGame:
    modes: list[str]

@dataclass
class CompetitiveData:
    games: dict[str, CompetitiveDataGame]

competitive_data = load_config("competitive.json", CompetitiveData)