from starlette.requests import Request
from starlette.routing import Route
from api.auth import require_logged_in, require_permission
from api.data import handle
from api.utils.responses import JSONResponse, bind_request_body
from common.auth import permissions
from common.data.commands import *
from common.data.models import *

@require_permission(permissions.MANAGE_USER_ROLES)
async def list_roles(request: Request) -> JSONResponse:
    roles = await handle(ListRolesCommand())
    return JSONResponse(roles)

@require_permission(permissions.MANAGE_USER_ROLES)
async def role_info(request: Request) -> JSONResponse:
    role_id = request.path_params['id']
    role_info = await handle(GetRoleInfoCommand(role_id))
    return JSONResponse(role_info)

@bind_request_body(GrantRoleRequestData)
@require_permission(permissions.MANAGE_USER_ROLES)
async def grant_role_to_player(request: Request, body: GrantRoleRequestData) -> JSONResponse:
    user_id = request.state.user.id
    command = GrantRoleCommand(user_id, body.player_id, body.role_name, body.expires_on)
    await handle(command)
    return JSONResponse({})

@bind_request_body(RemoveRoleRequestData)
@require_permission(permissions.MANAGE_USER_ROLES)
async def remove_role_from_player(request: Request, body: RemoveRoleRequestData) -> JSONResponse:
    user_id = request.state.user.id
    command = RemoveRoleCommand(user_id, body.player_id, body.role_name)
    await handle(command)
    return JSONResponse({})

routes = [
    Route('/api/roles', list_roles),
    Route('/api/roles/{id:int}', role_info),
    Route('/api/roles/grant', grant_role_to_player, methods=['POST']),
    Route('/api/roles/remove', remove_role_from_player, methods=['POST'])
]
