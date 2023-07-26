from starlette.requests import Request
from starlette.routing import Route
from api.auth import require_logged_in
from api.data import handle
from api.utils.responses import JSONResponse
from common.data.commands import GetUserDataFromIdCommand, GetUserPlayerDataFromIdCommand, GetPlayerDetailedCommand
from common.data.models import UserPlayer

@require_logged_in
async def current_user(request: Request) -> JSONResponse:
    user = await handle(GetUserDataFromIdCommand(request.state.user.id))
    return JSONResponse(user)

@require_logged_in
async def current_user_and_player(request: Request) -> JSONResponse:
    user = await handle(GetUserDataFromIdCommand(request.state.user.id))
    player = None
    if user.player_id:
        player = await handle(GetPlayerDetailedCommand(user.player_id))
    return JSONResponse(UserPlayer(user.id, user.player_id, player))

routes = [
    Route('/api/user/me', current_user),
    Route('/api/user/me/player', current_user_and_player)
]
