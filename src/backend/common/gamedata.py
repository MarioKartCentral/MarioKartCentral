import pkgutil
import json
from typing import TypedDict, Literal

Lang = Literal["en"]
Translations = dict[Lang, str]

class Cup(TypedDict):
    name: Translations

class Track(TypedDict):
    id: str
    name: Translations

class Game(TypedDict):
    cups: list[Cup]
    tracks: list[Track]
    
class GameData(TypedDict):
    games: dict[str, Game]

gamedata_bytes = pkgutil.get_data("common", "assets/game_data.json")
if gamedata_bytes is None:
    raise Exception("Unable to load game data json")

gamedata: GameData = json.loads(gamedata_bytes.decode())
