from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from api.auth import permissions, require_permission
from api.redis import redis_conn

@require_permission(permissions.WRITE_REDIS)
async def redis_write(request: Request) -> JSONResponse:
    text = request.path_params['text']
    await redis_conn.append("test", text)
    values = await redis_conn.get("test")
    return JSONResponse({'test': values})

routes = [
    Route('/api/redis_write/{text:str}', redis_write),
]