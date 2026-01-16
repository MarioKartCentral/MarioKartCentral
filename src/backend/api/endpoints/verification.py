from starlette.requests import Request
from starlette.routing import Route
from api.auth import require_permission
from api.data import handle
from api.utils.responses import JSONResponse, bind_request_body
from common.data.commands import *
from common.data.models import RequestVerificationRequestData

@bind_request_body(RequestVerificationRequestData)
@require_permission(permissions.REQUEST_VERIFICATION, check_denied_only=True)
async def request_verification(request: Request, body: RequestVerificationRequestData) -> JSONResponse:
    command = RequestVerificationCommand(request.state.user.player_id, body.friend_code_ids, body.verify_player)
    await handle(command)
    return JSONResponse({})

routes = [
    Route('/api/verification/request', request_verification, methods=['POST']),
]