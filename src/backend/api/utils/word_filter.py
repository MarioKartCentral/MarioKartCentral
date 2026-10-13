from collections.abc import Awaitable, Callable
from typing import Concatenate
from starlette.requests import Request
from starlette.responses import Response
from api.data import State
from common.data.commands import *


def check_word_filter[**P](handle_request: Callable[Concatenate[Request[State], P], Awaitable[Response]]):
    async def wrapper(request: Request[State], *args: P.args, **kwargs: P.kwargs):
        body = await request.json()
        await request.state.command_handler.handle(CheckWordFilterCommand(body))
        return await handle_request(request, *args, **kwargs)
    return wrapper
