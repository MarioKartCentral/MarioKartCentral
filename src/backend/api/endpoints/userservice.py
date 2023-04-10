from starlette.requests import Request
from starlette.routing import Route
from api.auth import require_logged_in
from api.data import handle
from api.utils.responses import JSONResponse
from common.data.commands import GetUserDataFromIdCommand

@require_logged_in
async def current_user(request: Request) -> JSONResponse:
    user = await handle(GetUserDataFromIdCommand(request.state.user.id))
    return JSONResponse(user)

routes = [
    Route('/api/user/me', current_user),
]
