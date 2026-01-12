from typing import Callable

def dispatch_notification_if(condition: Callable):
    def decorator(dispatch: Callable):
        async def wrapper(*args, **kwargs):
            if await condition(*args, **kwargs):
                return await dispatch(*args, **kwargs)
        return wrapper
    return decorator
