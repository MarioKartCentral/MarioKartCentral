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

routes = [
    Route('/api/moderator/session_matches', view_session_matches)
]