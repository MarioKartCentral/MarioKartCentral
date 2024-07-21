from starlette.requests import Request
from starlette.routing import Route
from api.auth import require_logged_in, require_permission
from api.data import handle
from api.utils.responses import JSONResponse
from common.auth import permissions
from common.data.commands import *

@require_logged_in
async def grant_role(request: Request) -> JSONResponse:
    body = await request.json()
    user_id = body["user_id"]
    role = body["role"]

    command = GrantRoleCommand(request.state.user.id, user_id, role)
    await handle(command)

    return JSONResponse({}, status_code=200)

@require_permission(permissions.MANAGE_USER_ROLES)
async def list_roles(request: Request) -> JSONResponse:
    roles = await handle(ListRolesCommand())
    return JSONResponse(roles)

@require_permission(permissions.MANAGE_USER_ROLES)
async def role_info(request: Request) -> JSONResponse:
    role_id = request.path_params['id']
    role_info = await handle(GetRoleInfoCommand(role_id))
    return JSONResponse(role_info)

routes = [
    Route('/api/user/grant_role', grant_role, methods=['POST']),
    Route('/api/roles', list_roles),
    Route('/api/roles/{id:int}', role_info)
]
