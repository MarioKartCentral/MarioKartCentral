from collections.abc import Awaitable, Callable

def dispatch_notification_if[**P](condition: Callable[P, Awaitable[bool]]):
    def decorator(dispatch: Callable[P, Awaitable[None]]) -> Callable[P, Awaitable[None]]:
        async def wrapper(*args: P.args, **kwargs: P.kwargs):
            if await condition(*args, **kwargs):
                return await dispatch(*args, **kwargs)
        return wrapper
    return decorator
