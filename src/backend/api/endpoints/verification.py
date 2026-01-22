from starlette.requests import Request
from starlette.routing import Route
from api.auth import require_permission
from api.data import handle
from api.utils.responses import JSONResponse, bind_request_body, bind_request_query
from common.data.commands import *
from common.data.models import RequestVerificationRequestData, PlayerVerificationFilter, UpdateVerificationsRequestData

@bind_request_body(RequestVerificationRequestData)
@require_permission(permissions.REQUEST_VERIFICATION, check_denied_only=True)
async def request_verification(request: Request, body: RequestVerificationRequestData) -> JSONResponse:
    command = RequestVerificationCommand(request.state.user.player_id, body.friend_code_ids, body.verify_player)
    await handle(command)
    return JSONResponse({})

@bind_request_query(PlayerVerificationFilter)
@require_permission(permissions.MANAGE_VERIFICATIONS)
async def list_player_verifications(request: Request, body: PlayerVerificationFilter) -> JSONResponse:
    command = ListPlayerVerificationsCommand(body)
    verifications = await handle(command)
    return JSONResponse(verifications)

@bind_request_body(UpdateVerificationsRequestData)
@require_permission(permissions.MANAGE_VERIFICATIONS)
async def update_verifications(request: Request, body: UpdateVerificationsRequestData) -> JSONResponse:
    command = UpdateVerificationsCommand(body.player_verifications, body.fc_verifications, request.state.user.player_id)
    await handle(command)
    return JSONResponse({})

routes = [
    Route('/api/verification/request', request_verification, methods=['POST']),
    Route('/api/verification/player_verifications', list_player_verifications),
    Route('/api/verification/update', update_verifications, methods=['POST']),
]