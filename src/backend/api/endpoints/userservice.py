from starlette.requests import Request
from starlette.routing import Route
from api.auth import inject_current_user, require_logged_in, require_permission
from api.data import State
from api.utils.responses import JSONResponse, bind_request_body, bind_request_query
from common.data.commands import *
from common.data.models import UserPlayer, EditUserRequestData, Problem
from common.auth import pw_hasher


@require_logged_in()
@inject_current_user
async def current_user(request: Request[State], user: User) -> JSONResponse:
    user_data = await request.state.command_handler.handle(GetUserDataFromIdCommand(user.id))
    if user_data is None:
        raise Problem("User is not logged in", status=401)
    return JSONResponse(user_data, headers={"Cache-Control": "private, max-age=60", "Vary": "Cookie"})


@require_logged_in()
@inject_current_user
async def current_user_and_player(request: Request[State], user: User) -> JSONResponse:
    user_data = await request.state.command_handler.handle(GetUserDataFromIdCommand(user.id))
    if user_data is None:
        raise Problem("User is not logged in", status=401)
    player = None
    if user_data.player_id:
        player = await request.state.command_handler.handle(GetPlayerDetailedCommand(user_data.player_id))
    user_roles, team_roles, series_roles, tournament_roles = await request.state.command_handler.handle(GetUserRolePermissionsCommand(user_data.id))
    mod_notifications = None
    token_count = 0
    if len(user_roles) > 0:
        mod_notifications = await request.state.command_handler.handle(GetModNotificationsCommand(user_roles))
        tokens = await request.state.command_handler.handle(GetUserAPITokensCommand(user_data.id))
        token_count = len(tokens)
    return JSONResponse(UserPlayer(user_data.id, user_data.player_id, user_data.email_confirmed, user_data.force_password_reset, player, user_roles, team_roles, series_roles, tournament_roles, mod_notifications, token_count), headers={"Cache-Control": "private, max-age=60", "Vary": "Cookie"})


@require_logged_in()
@inject_current_user
async def player_invites(request: Request[State], user: User) -> JSONResponse:
    if user.player_id is None:
        raise Problem("Bad Request", status=400)
    invites = await request.state.command_handler.handle(GetInvitesForPlayerCommand(user.player_id))
    return JSONResponse(invites)


@bind_request_query(UserFilter)
@require_permission(permissions.EDIT_USER)
async def list_users(request: Request[State], body: UserFilter) -> JSONResponse:
    command = ListUsersCommand(body)
    user_list = await request.state.command_handler.handle(command)
    return JSONResponse(user_list)


@bind_request_body(EditUserRequestData)
@require_permission(permissions.EDIT_USER)
@inject_current_user
async def edit_user(request: Request[State], user: User, body: EditUserRequestData) -> JSONResponse:
    if body.password:
        password_hash = pw_hasher.hash(body.password)
    else:
        password_hash = None
    command = EditUserCommand(user.id, body.user_id, body.email,
                              password_hash, body.email_confirmed, body.force_password_reset)
    await request.state.command_handler.handle(command)
    return JSONResponse({})


@require_permission(permissions.EDIT_USER)
@inject_current_user
async def view_user(request: Request[State], user: User) -> JSONResponse:
    user_id = request.path_params['user_id']
    mod_user_id = user.id
    command = ViewUserCommand(user_id, mod_user_id)
    user_info = await request.state.command_handler.handle(command)
    return JSONResponse(user_info)

routes = [
    Route('/api/user/me', current_user),
    Route('/api/user/me/player', current_user_and_player),
    Route('/api/user/me/invites', player_invites),
    Route('/api/user/list', list_users),
    Route('/api/user/edit', edit_user, methods=['POST']),
    Route('/api/user/{user_id:int}', view_user)
]
