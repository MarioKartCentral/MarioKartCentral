from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route
from starlette.background import BackgroundTask
from api.auth import require_permission, require_logged_in
from api.data import handle
from api.utils.responses import JSONResponse, bind_request_body, bind_request_query
from common.auth import permissions
from common.data.commands import *
from common.data.models import *
import common.data.notifications as notifications


@bind_request_body(CreatePlayerRequestData)
@require_logged_in
async def create_player(request: Request, body: CreatePlayerRequestData) -> Response:
    command = CreatePlayerCommand(request.state.user.id, body.name, body.country_code, body.friend_codes, False, False)
    player = await handle(command)
    return JSONResponse(player, status_code=201)

@bind_request_body(CreatePlayerRequestData)
@require_permission(permissions.MANAGE_SHADOW_PLAYERS)
async def create_shadow_player(request: Request, body: CreatePlayerRequestData) -> JSONResponse:
    command = CreatePlayerCommand(None, body.name, body.country_code, body.friend_codes, body.is_hidden, True)
    player = await handle(command)
    return JSONResponse(player, status_code=201)

@bind_request_body(EditPlayerRequestData)
@require_permission(permissions.EDIT_PLAYER)
async def edit_player(request: Request, body: EditPlayerRequestData) -> Response:    
    command = UpdatePlayerCommand(body)
    succeeded = await handle(command)
    if not succeeded:
        raise Problem("Player not found", status=404)
    
    return JSONResponse({}, status_code=200)

async def view_player(request: Request) -> Response:
    command = GetPlayerDetailedCommand(request.path_params['id'])
    player_detailed = await handle(command)
    if player_detailed is None:
        raise Problem("Player not found", status=404)

    return JSONResponse(player_detailed)

@bind_request_query(PlayerFilter)
async def list_players(_: Request, filter: PlayerFilter) -> Response:
    command = ListPlayersCommand(filter)
    players = await handle(command)
    return JSONResponse(players)

@bind_request_body(CreateFriendCodeRequestData)
@require_permission(permissions.EDIT_PROFILE, check_denied_only=True)
async def create_fc(request: Request, body: CreateFriendCodeRequestData) -> JSONResponse:
    command = CreateFriendCodeCommand(request.state.user.player_id, body.fc, body.game, False, body.is_primary, True, body.description, False)
    await handle(command)
    return JSONResponse({})

@bind_request_body(ForceCreateFriendCodeRequestData)
@require_permission(permissions.EDIT_PLAYER)
async def force_create_fc(request: Request, body: ForceCreateFriendCodeRequestData) -> JSONResponse:
    async def notify():
        user_id = await handle(GetUserIdFromPlayerIdCommand(body.player_id))
        await handle(DispatchNotificationCommand([user_id], notifications.FORCE_ADD_FRIEND_CODE, {'game': body.game}, f'/registry/players/profile?id={body.player_id}', notifications.INFO))

    command = CreateFriendCodeCommand(body.player_id, body.fc, body.game, False, body.is_primary, True, body.description, True)
    await handle(command)
    return JSONResponse({}, background=BackgroundTask(notify))

@bind_request_body(ForceEditFriendCodeRequestData)
@require_permission(permissions.EDIT_PLAYER)
async def force_edit_fc(request: Request, body: ForceEditFriendCodeRequestData) -> JSONResponse:
    async def notify():
        game = await handle(GetGameFromPlayerFCCommand(body.id))
        user_id = await handle(GetUserIdFromPlayerIdCommand(body.player_id))
        await handle(DispatchNotificationCommand([user_id], notifications.FORCE_EDIT_FRIEND_CODE, {'game': game}, f'/registry/players/profile?id={body.player_id}', notifications.INFO))

    command = EditFriendCodeCommand(body.player_id, body.id, body.fc, body.is_primary, body.is_active, body.description)
    await handle(command)
    return JSONResponse({}, background=BackgroundTask(notify))

@bind_request_body(EditMyFriendCodeRequestData)
@require_permission(permissions.EDIT_PROFILE, check_denied_only=True)
async def edit_my_fc(request: Request, body: EditMyFriendCodeRequestData) -> JSONResponse:
    player_id = request.state.user.player_id
    command = EditFriendCodeCommand(player_id, body.id, None, body.is_primary, None, body.description)
    await handle(command)
    return JSONResponse({})

@bind_request_body(EditPrimaryFriendCodeRequestData)
@require_logged_in
async def set_primary_fc(request: Request, body: EditPrimaryFriendCodeRequestData) -> JSONResponse:
    command = SetPrimaryFCCommand(body.id, request.state.user.player_id)
    await handle(command)
    return JSONResponse({})

@bind_request_body(ModEditPrimaryFriendCodeRequestData)
@require_logged_in
async def force_primary_fc(request: Request, body: ModEditPrimaryFriendCodeRequestData) -> JSONResponse:
    async def notify():
        user_id = await handle(GetUserIdFromPlayerIdCommand(body.player_id))
        await handle(DispatchNotificationCommand([user_id], notifications.FORCE_PRIMARY_FRIEND_CODE, {}, f'/registry/players/profile?id={body.player_id}', notifications.INFO))

    command = SetPrimaryFCCommand(body.id, body.player_id)
    await handle(command)
    return JSONResponse({}, background=BackgroundTask(notify))

@bind_request_body(PlayerRequestNameRequestData)
@require_permission(permissions.EDIT_PROFILE, check_denied_only=True)
async def request_edit_player_name(request: Request, body: PlayerRequestNameRequestData) -> JSONResponse:
    command = RequestEditPlayerNameCommand(request.state.user.player_id, body.name)
    await handle(command)
    return JSONResponse({})

@require_permission(permissions.EDIT_PLAYER)
async def get_pending_player_name_requests(request: Request) -> JSONResponse:
    command = ListPlayerNameRequestsCommand("pending")
    changes = await handle(command)
    return JSONResponse(changes)

@bind_request_body(ApprovePlayerNameRequestData)
@require_permission(permissions.EDIT_PLAYER)
async def approve_player_name_request(request: Request, body: ApprovePlayerNameRequestData) -> JSONResponse:
    async def notify():
        data = await handle(GetNotificationDataFromNameChangeRequestCommand(body.request_id))
        await handle(DispatchNotificationCommand([data.user_id], notifications.NAME_CHANGE_APPROVED, {}, f'/registry/players/profile?id={data.player_id}', notifications.SUCCESS))

    command = ApprovePlayerNameRequestCommand(body.request_id)
    await handle(command)
    return JSONResponse({}, background=BackgroundTask(notify))

@bind_request_body(ApprovePlayerNameRequestData)
@require_permission(permissions.EDIT_PLAYER)
async def deny_player_name_request(request: Request, body: ApprovePlayerNameRequestData) -> JSONResponse:
    async def notify():
        data = await handle(GetNotificationDataFromNameChangeRequestCommand(body.request_id))
        await handle(DispatchNotificationCommand([data.user_id], notifications.NAME_CHANGE_DENIED, {}, f'/registry/players/profile?id={data.player_id}', notifications.WARNING))

    command = DenyPlayerNameRequestCommand(body.request_id)
    await handle(command)
    return JSONResponse({}, background=BackgroundTask(notify))

@bind_request_body(ClaimPlayerRequestData)
@require_logged_in
async def claim_player(request: Request, body: ClaimPlayerRequestData) -> JSONResponse:
    command = ClaimPlayerCommand(request.state.user.player_id, body.player_id)
    await handle(command)
    return JSONResponse({})

@bind_request_body(ApproveDenyPlayerClaimRequestData)
@require_permission(permissions.MANAGE_SHADOW_PLAYERS)
async def approve_player_claim(request: Request, body: ApproveDenyPlayerClaimRequestData) -> JSONResponse:
    command = ApprovePlayerClaimCommand(body.claim_id)
    player_id, user_id, claimed_player_name = await handle(command)
    async def notify():
        content_args = {"player_name": claimed_player_name}
        await handle(DispatchNotificationCommand([user_id], notifications.PLAYER_CLAIM_APPROVED, content_args, f'/registry/players/profile?id={player_id}', notifications.SUCCESS))
    return JSONResponse({}, background=BackgroundTask(notify))

@bind_request_body(ApproveDenyPlayerClaimRequestData)
@require_permission(permissions.MANAGE_SHADOW_PLAYERS)
async def deny_player_claim(request: Request, body: ApproveDenyPlayerClaimRequestData) -> JSONResponse:
    command = DenyPlayerClaimCommand(body.claim_id)
    player_id, user_id, claimed_player_name = await handle(command)
    async def notify():
        content_args = {"player_name": claimed_player_name}
        await handle(DispatchNotificationCommand([user_id], notifications.PLAYER_CLAIM_DENIED, content_args, f'/registry/players/profile?id={player_id}', notifications.WARNING))
    return JSONResponse({}, background=BackgroundTask(notify))

@require_permission(permissions.MANAGE_SHADOW_PLAYERS)
async def list_player_claims(request: Request) -> JSONResponse:
    command = ListPlayerClaimsCommand()
    claims = await handle(command)
    return JSONResponse(claims)

routes = [
    Route('/api/registry/players/create', create_player, methods=['POST']),
    Route('/api/registry/players/createShadowPlayer', create_shadow_player, methods=['POST']),
    Route('/api/registry/players/edit', edit_player, methods=['POST']),
    Route('/api/registry/players/{id:int}', view_player),
    Route('/api/registry/players', list_players),
    Route('/api/registry/addFriendCode', create_fc, methods=['POST']),
    Route('/api/registry/forceAddFriendCode', force_create_fc, methods=['POST']), # dispatches notification
    Route('/api/registry/forceEditFriendCode', force_edit_fc, methods=['POST']), # dispatches notification
    Route('/api/registry/editFriendCode', edit_my_fc, methods=['POST']),
    Route('/api/registry/setPrimaryFriendCode', set_primary_fc, methods=['POST']),
    Route('/api/registry/forcePrimaryFriendCode', force_primary_fc, methods=['POST']), # dispatches notification
    Route('/api/registry/players/requestName', request_edit_player_name, methods=['POST']),
    Route('/api/registry/players/pendingNameChanges', get_pending_player_name_requests),
    Route('/api/registry/players/approveNameChange', approve_player_name_request, methods=['POST']), # dispatches notification
    Route('/api/registry/players/denyNameChange', deny_player_name_request, methods=['POST']), # dispatches notification
    Route('/api/registry/players/claim', claim_player, methods=['POST']),
    Route('/api/registry/players/approveClaim', approve_player_claim, methods=['POST']),
    Route('/api/registry/players/denyClaim', deny_player_claim, methods=['POST']),
    Route('/api/registry/players/claims', list_player_claims),
]