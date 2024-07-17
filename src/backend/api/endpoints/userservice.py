from starlette.requests import Request
from starlette.routing import Route
from api.auth import require_logged_in
from api.data import handle
from api.utils.responses import JSONResponse, bind_request_query
from common.data.commands import GetUserDataFromIdCommand, GetPlayerDetailedCommand, CheckPermissionsCommand, GetModNotificationsCommand, GetInvitesForPlayerCommand
from common.data.models import UserPlayer, PermissionsCheck
from common.data.models.common import Problem

@require_logged_in
async def current_user(request: Request) -> JSONResponse:
    user = await handle(GetUserDataFromIdCommand(request.state.user.id))
    if user is None:
        raise Problem("User is not logged in", status=401)
    return JSONResponse(user)

#@bind_request_query(PermissionsCheck)
@require_logged_in
async def current_user_and_player(request: Request) -> JSONResponse:
    user = await handle(GetUserDataFromIdCommand(request.state.user.id))
    if user is None:
        raise Problem("User is not logged in", status=401)
    player = None
    if user.player_id:
        player = await handle(GetPlayerDetailedCommand(user.player_id))
    valid_perms, team_perms, series_perms, tournament_perms = await handle(CheckPermissionsCommand(user.id))
    mod_notifications = None
    if len(valid_perms) > 0:
        mod_notifications = await handle(GetModNotificationsCommand(valid_perms))
    return JSONResponse(UserPlayer(user.id, user.player_id, player, valid_perms, team_perms, series_perms, tournament_perms, mod_notifications))

@require_logged_in
async def player_invites(request: Request) -> JSONResponse:
    invites = await handle(GetInvitesForPlayerCommand(request.state.user.player_id))
    return JSONResponse(invites)

routes = [
    Route('/api/user/me', current_user),
    Route('/api/user/me/player', current_user_and_player),
    Route('/api/user/me/invites', player_invites)
]
