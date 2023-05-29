from dataclasses import dataclass
from common.data.models.common import Game, GameMode


@dataclass
class SeriesRequestData():
    series_name: str
    url: str | None
    game: Game
    mode: GameMode
    is_historical: bool
    is_public: bool
    description: str
    logo: str | None
    ruleset: str
    organizer: str
    location: str
    
@dataclass
class Series():
    id: int
    series_name: str
    url: str | None
    game: Game
    mode: GameMode
    is_historical: bool
    is_public: bool
    description: str
    logo: str | None

@dataclass
class SeriesFilter():
    is_historical: bool | None = None
    is_public: bool | None = None
    game: Game | None = None
    mode: GameMode | None = None