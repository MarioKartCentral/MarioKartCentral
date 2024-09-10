from starlette.requests import Request
from starlette.routing import Route
from api.auth import require_logged_in
from api.data import handle
from api.utils.responses import JSONResponse
from common.data.commands import *
from common.data.models import UserPlayer
from common.data.models.common import Problem

@require_logged_in
async def current_user(request: Request) -> JSONResponse:
    user = await handle(GetUserDataFromIdCommand(request.state.user.id))
    if user is None:
        raise Problem("User is not logged in", status=401)
    return JSONResponse(user)

@require_logged_in
async def current_user_and_player(request: Request) -> JSONResponse:
    user = await handle(GetUserDataFromIdCommand(request.state.user.id))
    if user is None:
        raise Problem("User is not logged in", status=401)
    player = None
    if user.player_id:
        player = await handle(GetPlayerDetailedCommand(user.player_id))
    user_roles, team_roles, series_roles, tournament_roles = await handle(GetUserRolePermissionsCommand(user.id))
    mod_notifications = None
    if len(user_roles) > 0:
        mod_notifications = await handle(GetModNotificationsCommand(user_roles))
    return JSONResponse(UserPlayer(user.id, user.player_id, player, user_roles, team_roles, series_roles, tournament_roles, mod_notifications))

@require_logged_in
async def player_invites(request: Request) -> JSONResponse:
    invites = await handle(GetInvitesForPlayerCommand(request.state.user.player_id))
    return JSONResponse(invites)

routes = [
    Route('/api/user/me', current_user),
    Route('/api/user/me/player', current_user_and_player),
    Route('/api/user/me/invites', player_invites)
]
