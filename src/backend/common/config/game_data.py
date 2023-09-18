from dataclasses import dataclass
from common.config.common import load_config

@dataclass
class GameDataGame:
    courses: list[str]

@dataclass
class GameData:
    games: dict[str, GameDataGame]

game_data = load_config("game_data.json", GameData)