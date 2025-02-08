from dataclasses import dataclass
from common.data.models.common import Game, GameMode

@dataclass
class SeriesDBFields():
    series_name: str
    url: str | None
    display_order: int
    game: Game
    mode: GameMode
    is_historical: bool
    is_public: bool
    short_description: str
    logo: str | None
    organizer: str
    location: str | None

@dataclass
class SeriesS3Fields():
    description: str
    ruleset: str

@dataclass
class SeriesRequestData(SeriesDBFields, SeriesS3Fields): pass
    
@dataclass
class EditSeriesRequestData(SeriesRequestData):
    series_id: int

@dataclass
class SeriesBasic:
    id: int
    series_name: str
    url: str | None
    display_order: int
    game: Game
    mode: GameMode
    is_historical: bool
    is_public: bool
    short_description: str
    logo: str | None
    organizer: str
    location: str | None

@dataclass
class Series(SeriesBasic):
    description: str
    ruleset: str

@dataclass
class SeriesFilter():
    name: str | None = None
    is_historical: bool | None = None
    is_public: bool | None = None
    game: Game | None = None
    mode: GameMode | None = None