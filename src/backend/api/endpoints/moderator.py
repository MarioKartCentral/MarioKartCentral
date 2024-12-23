from starlette.requests import Request
from starlette.routing import Route
from api.auth import require_permission
from api.data import handle
from api.utils.responses import JSONResponse, bind_request_query
from common.auth import permissions
from common.data.commands import *
from common.data.models import *

@bind_request_query(SessionMatchFilter)
@require_permission(permissions.VIEW_ACCOUNT_MATCHES)
async def view_session_matches(request: Request, filter: SessionMatchFilter) -> JSONResponse:
    command = GetSessionMatchesCommand(filter)
    match_list = await handle(command)
    return JSONResponse(match_list)

@require_permission(permissions.VIEW_ACCOUNT_MATCHES)
async def view_player_session_matches(request: Request) -> JSONResponse:
    player_id = int(request.path_params['player_id'])
    command = GetPlayerSessionMatchesCommand(player_id)
    matches = await handle(command)
    return JSONResponse(matches)

@bind_request_query(IPMatchFilter)
@require_permission(permissions.VIEW_ACCOUNT_MATCHES)
async def view_ip_matches(request: Request, filter: IPMatchFilter) -> JSONResponse:
    # used to determine if IP addresses are included in the response or not
    is_privileged = await handle(CheckUserHasPermissionCommand(request.state.user.id, permissions.VIEW_IP_ADDRESSES))
    command = GetIPMatchesCommand(filter, is_privileged)
    match_list = await handle(command)
    return JSONResponse(match_list)

@require_permission(permissions.VIEW_ACCOUNT_MATCHES)
async def view_player_ip_matches(request: Request) -> JSONResponse:
    player_id = int(request.path_params['player_id'])
    # used to determine if IP addresses are included in the response or not
    is_privileged = await handle(CheckUserHasPermissionCommand(request.state.user.id, permissions.VIEW_IP_ADDRESSES))
    command = GetPlayerIPMatchesCommand(player_id, is_privileged)
    matches = await handle(command)
    return JSONResponse(matches)

routes = [
    Route('/api/moderator/session_matches', view_session_matches),
    Route('/api/moderator/players/{player_id:int}/session_matches', view_player_session_matches),
    Route('/api/moderator/ip_matches', view_ip_matches),
    Route('/api/moderator/players/{player_id:int}/ip_matches', view_player_ip_matches)
]