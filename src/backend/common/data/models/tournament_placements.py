from dataclasses import dataclass
from typing import List

@dataclass
class Placements():
    squad_id: int
    placement: int
    placement_description: str | None

@dataclass
class SetPlacements():
    placements: List[Placements]

@dataclass
class GetPlacementsData():
    placements: List[Placements]