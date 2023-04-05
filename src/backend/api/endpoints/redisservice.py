from starlette.requests import Request
from starlette.routing import Route
from api.auth import require_permission
from api.data import redis_conn
from api.utils.responses import JSONResponse
from common.auth import permissions

@require_permission(permissions.WRITE_REDIS)
async def redis_write(request: Request) -> JSONResponse:
    text = request.path_params['text']
    await redis_conn.append("test", text)
    values = await redis_conn.get("test")
    return JSONResponse({'test': values})

routes = [
    Route('/api/redis_write/{text:str}', redis_write),
]