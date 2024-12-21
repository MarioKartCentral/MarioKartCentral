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

routes = [
    Route('/api/moderator/session_matches', view_session_matches),
    Route('/api/moderator/players/{player_id:int}/session_matches', view_player_session_matches)
]