from dataclasses import dataclass

from common.data.validators import validate_game_and_mode


@dataclass
class SeriesRequestData():
    series_name: str
    url: str | None
    game: str
    mode: str
    is_historical: bool
    is_public: bool
    description: str
    logo: str | None
    ruleset: str
    organizer: str
    location: str

    def __post_init__(self):
        validate_game_and_mode(self.game, self.mode)
    
@dataclass
class Series():
    id: int
    series_name: str
    url: str | None
    game: str
    mode: str
    is_historical: bool
    is_public: bool
    description: str
    logo: str | None

    def __post_init__(self):
        validate_game_and_mode(self.game, self.mode)

@dataclass
class SeriesFilter():
    is_historical: bool | None = None
    is_public: bool | None = None
    game: str | None = None
    mode: str | None = None

    def __post_init__(self):
        if self.game is not None and self.mode is not None:
            validate_game_and_mode(self.game, self.mode)