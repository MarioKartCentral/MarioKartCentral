from dataclasses import dataclass
from typing import Literal

from common.data.models.common import Game


@dataclass
class Record:
    player_id: int
    type: str
    game: Game
    time: str
    time_ms: float
    id: int = 0
    version: int = 0
    track: str | None = None
    cc: Literal[150, 200] | None = None