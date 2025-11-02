from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any, Concatenate
import msgspec
from starlette.requests import Request
from starlette.responses import Response, JSONResponse as StarletteJSONResponse

from common.data.models import Problem

@dataclass
class RouteSpecTypes:
    query_type: type[Any] | None = None
    body_type: type[Any] | None = None


def bind_request_query[T](type: type[T]):
    def decorator[**P](handle_request: Callable[Concatenate[Request, T, P], Awaitable[Response]]):
        async def wrapper(request: Request, *args: P.args, **kwargs: P.kwargs):
            all_params = dict(request.query_params.__dict__)
            all_params.update(request.path_params)

            query_as_json = msgspec.json.encode(dict(request.query_params))

            try:
                body = msgspec.json.decode(query_as_json, type=type, strict=False)
            except msgspec.ValidationError as e:
                raise Problem("Invalid query string parameter", detail=str(e), status=400)

            return await handle_request(request, body, *args, **kwargs)

        spec_types = RouteSpecTypes(query_type=type, body_type=None)
        if hasattr(handle_request, 'spec_types'):
            existing_spec_types: RouteSpecTypes = getattr(handle_request, 'spec_types')
            spec_types.body_type = existing_spec_types.body_type

        setattr(wrapper, 'spec_types', spec_types)
        return wrapper
    return decorator

def bind_request_body[T](type: type[T]):
    def decorator[**P](handle_request: Callable[Concatenate[Request, T, P], Awaitable[Response]]):
        async def wrapper(request: Request, *args: P.args, **kwargs: P.kwargs) -> Response:
            body_bytes = await request.body()
            try:
                body = msgspec.json.decode(body_bytes, type=type)
            except msgspec.ValidationError as e:
                raise Problem("Invalid request body", detail=str(e), status=400)

            return await handle_request(request, body, *args, **kwargs)

        spec_types = RouteSpecTypes(query_type=None, body_type=type)
        if hasattr(handle_request, 'spec_types'):
            existing_spec_types: RouteSpecTypes = getattr(handle_request, 'spec_types')
            spec_types.query_type = existing_spec_types.query_type

        setattr(wrapper, 'spec_types', spec_types)
        return wrapper
    return decorator


class JSONResponse(StarletteJSONResponse):
    def render(self, content: Any) -> bytes:
        return msgspec.json.encode(content)

class ProblemResponse(JSONResponse):
    media_type = "application/problem+json"

    def __init__(self, problem: Problem):
        super().__init__(problem, problem.status)