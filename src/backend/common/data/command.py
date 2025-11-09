from abc import ABC, abstractmethod
from typing import Any

class Command[T](ABC):
    @abstractmethod
    async def handle(self, *args: Any, **kwargs: Any) -> T:
        pass