from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route
from api.auth import require_permission, require_logged_in
from api.data import handle
from api.utils.responses import JSONResponse, bind_request_body, bind_request_query
from common.auth import permissions
from common.data.commands import *
from common.data.models import *


@bind_request_body(CreatePlayerRequestData)
@require_logged_in
async def create_player(request: Request, body: CreatePlayerRequestData) -> Response:
    command = CreatePlayerCommand(request.state.user.id, body)
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
@require_logged_in
async def create_fc(request: Request, body: CreateFriendCodeRequestData) -> JSONResponse:
    command = CreateFriendCodeCommand(request.state.user.player_id, body.fc, body.game, False, body.is_primary, True, body.description, False)
    await handle(command)
    return JSONResponse({})

@bind_request_body(EditFriendCodeRequestData)
@require_logged_in
async def edit_fc(request: Request, body: EditFriendCodeRequestData) -> JSONResponse:
    command = EditFriendCodeCommand(body.id, body.fc, body.game, body.is_active, body.description)
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
    command = SetPrimaryFCCommand(body.id, body.player_id)
    await handle(command)
    return JSONResponse({})

routes = [
    Route('/api/registry/players/create', create_player, methods=['POST']),
    Route('/api/registry/players/edit', edit_player, methods=['POST']),
    Route('/api/registry/players/{id:int}', view_player),
    Route('/api/registry/players', list_players),
    Route('/api/registry/addFriendCode', create_fc, methods=['POST']),
    Route('/api/registry/forceEditFriendCode', edit_fc, methods=['POST']),
    Route('/api/registry/setPrimaryFriendCode', set_primary_fc, methods=['POST']),
    Route('/api/registry/forcePrimaryFriendCode', force_primary_fc, methods=['POST'])
]