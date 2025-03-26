from starlette.requests import Request
from starlette.routing import Route
from api.auth import require_logged_in, require_permission
from api.data import handle
from api.utils.responses import JSONResponse, bind_request_body, bind_request_query
from common.data.commands import *
from common.data.models import UserPlayer, EditUserRequestData
from common.data.models.common import Problem
from common.auth import pw_hasher

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
    return JSONResponse(UserPlayer(user.id, user.player_id, user.email_confirmed, user.force_password_reset, player, user_roles, team_roles, series_roles, tournament_roles, mod_notifications))

@require_logged_in
async def player_invites(request: Request) -> JSONResponse:
    invites = await handle(GetInvitesForPlayerCommand(request.state.user.player_id))
    return JSONResponse(invites)

@bind_request_query(UserFilter)
@require_permission(permissions.EDIT_USER)
async def list_users(request: Request, body: UserFilter) -> JSONResponse:
    command = ListUsersCommand(body)
    user_list = await handle(command)
    return JSONResponse(user_list)

@bind_request_body(EditUserRequestData)
@require_permission(permissions.EDIT_USER)
async def edit_user(request: Request, body: EditUserRequestData) -> JSONResponse:
    if body.password:
        password_hash = pw_hasher.hash(body.password)
    else:
        password_hash = None
    command = EditUserCommand(request.state.user.id, body.user_id, body.email, password_hash, body.email_confirmed, body.force_password_reset)
    await handle(command)
    return JSONResponse({})

@require_permission(permissions.EDIT_USER)
async def view_user(request: Request) -> JSONResponse:
    user_id = request.path_params['user_id']
    command = ViewUserCommand(user_id)
    user = await handle(command)
    return JSONResponse(user)

routes = [
    Route('/api/user/me', current_user),
    Route('/api/user/me/player', current_user_and_player),
    Route('/api/user/me/invites', player_invites),
    Route('/api/user/list', list_users),
    Route('/api/user/edit', edit_user, methods=['POST']),
    Route('/api/user/{user_id:int}', view_user)
]
