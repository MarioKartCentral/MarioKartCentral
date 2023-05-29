from dataclasses import dataclass
from typing import Literal


@dataclass
class Notification:
    id: int
    type: int
    content: str
    created_date: int
    is_read: bool

@dataclass
class NotificationFilter:
    is_read: Literal['0', '1'] | None = None
    type: str | None = None # separate multiple types with commas
    before: str | None = None
    after: str | None = None

@dataclass
class MarkAsReadRequestData:
    is_read: bool
