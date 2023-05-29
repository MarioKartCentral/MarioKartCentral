from dataclasses import dataclass
from typing import Any, Dict, Literal


@dataclass
class Problem(Exception):
    """
    A schema for describing an error, based on RFC-7807: https://www.rfc-editor.org/rfc/rfc7807

    title: 
        A short, human-readable explanation of the error.
        The title should have the same value for all instances of this error.

    detail:
        An optional, more detailed human-readable explanation of the error.
        Additional information specific to this instance of the error can be included.

    data:
        An optional bag of additional data to go with the error
    """
    title: str
    detail: str | None = None
    status: int = 500
    data: Dict[str, Any] | None = None

Game = Literal["mkw", "mk7", "mk8", "mk8dx", "mkt"]
GameMode = Literal["150cc", "200cc", "rt", "ct"]
Approval = Literal["approved", "pending", "denied"]