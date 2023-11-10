from dataclasses import dataclass
from common.data.models.common import Game, GameMode


@dataclass
class SeriesRequestData():
    series_name: str
    url: str | None
    display_order: int
    game: Game
    mode: GameMode
    is_historical: bool
    is_public: bool
    description: str
    logo: str | None
    ruleset: str
    organizer: str
    location: str | None
    
@dataclass
class Series():
    id: int
    series_name: str
    url: str | None
    display_order: int
    game: Game
    mode: GameMode
    is_historical: bool
    is_public: bool
    description: str
    ruleset: str
    logo: str | None

@dataclass
class SeriesFilter():
    name: str | None = None
    is_historical: bool | None = None
    is_public: bool | None = None
    game: Game | None = None
    mode: GameMode | None = None