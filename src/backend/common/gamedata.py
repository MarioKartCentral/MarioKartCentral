import pkgutil
import json
from typing import TypedDict, List, Dict, Literal

Lang = Literal["en"]
Translations = Dict[Lang, str]

class Cup(TypedDict):
    name: Translations

class Track(TypedDict):
    id: str
    name: Translations

class Game(TypedDict):
    cups: List[Cup]
    tracks: List[Track]
    
class GameData(TypedDict):
    games: Dict[str, Game]

gamedata_bytes = pkgutil.get_data("common", "assets/game_data.json")
if gamedata_bytes is None:
    raise Exception("Unable to load game data json")

gamedata: GameData = json.loads(gamedata_bytes.decode())
