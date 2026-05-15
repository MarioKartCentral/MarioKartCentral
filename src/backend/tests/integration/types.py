from typing import Awaitable, Callable
from starlette.testclient import TestClient
UserClientFactory = Callable[[str | None], Awaitable[TestClient]]
