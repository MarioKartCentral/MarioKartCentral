from collections.abc import Awaitable, Callable
from typing import Concatenate
from starlette.requests import Request
from starlette.responses import Response
from common.data.commands import *
from api.data import handle

def check_word_filter[**P](handle_request: Callable[Concatenate[Request, P], Awaitable[Response]]):
    async def wrapper(request: Request, *args: P.args, **kwargs: P.kwargs):
        body = await request.json()
        await handle(CheckWordFilterCommand(body))
        return await handle_request(request, *args, **kwargs)
    return wrapper