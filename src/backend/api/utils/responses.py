from typing import Any
import orjson
from starlette.responses import JSONResponse

class OrjsonResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        return orjson.dumps(content)

class ProblemJsonResponse(OrjsonResponse):
    media_type = "application/problem+json"