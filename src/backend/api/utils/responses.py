from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Concatenate, ParamSpec, Type, TypeVar
import msgspec
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from common.data.models import Problem

TBind = TypeVar("TBind")
P = ParamSpec('P')

@dataclass
class RouteSpecTypes:
    query_type: type | None = None
    body_type: type | None = None

def bind_request_query(type: Type[TBind]):
    def decorator(handle_request: Callable[Concatenate[Request, TBind, P], Awaitable[Response]]):
        async def wrapper(request: Request, *args: P.args, **kwargs: P.kwargs):
            all_params = dict(request.query_params.__dict__)
            all_params.update(request.path_params)

            query_as_json = msgspec.json.encode(dict(request.query_params))

            try:
                body = msgspec.json.decode(query_as_json, type=type)
            except msgspec.ValidationError as e:
                raise Problem("Invalid query string parameter", detail=str(e), status=400)

            return await handle_request(request, body, *args, **kwargs)

        spec_types = RouteSpecTypes(query_type=type, body_type=None)
        if hasattr(handle_request, 'spec_types'):
            spec_types.body_type = handle_request.spec_types.body_type

        wrapper.spec_types = spec_types
        return wrapper
    return decorator

def bind_request_body(type: Type[TBind]):
    def decorator(handle_request: Callable[Concatenate[Request, TBind, P], Awaitable[Response]]):
        async def wrapper(request: Request, *args: P.args, **kwargs: P.kwargs):
            body_bytes = await request.body()
            try:
                body = msgspec.json.decode(body_bytes, type=type)
            except msgspec.ValidationError as e:
                raise Problem("Invalid request body", detail=str(e), status=400)

            return await handle_request(request, body, *args, **kwargs)

        spec_types = RouteSpecTypes(query_type=None, body_type=type)
        if hasattr(handle_request, 'spec_types'):
            spec_types.query_type = handle_request.spec_types.query_type

        wrapper.spec_types = spec_types
        return wrapper
    return decorator


class JSONResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        return msgspec.json.encode(content)

class ProblemResponse(JSONResponse):
    media_type = "application/problem+json"

    def __init__(self, problem: Problem):
        super().__init__(problem, problem.status)