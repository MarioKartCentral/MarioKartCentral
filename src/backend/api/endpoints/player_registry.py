from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route
from api.auth import require_permission, require_logged_in
from api.data import handle
from api.utils.responses import JSONResponse, bind_request_body, bind_request_query
from common.auth import permissions
from common.data.commands import CreatePlayerCommand, GetPlayerDetailedCommand, ListPlayersCommand, UpdatePlayerCommand
from common.data.models import CreatePlayerRequestData, EditPlayerRequestData, PlayerFilter, Problem


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

routes = [
    Route('/api/registry/players/create', create_player, methods=['POST']),
    Route('/api/registry/players/edit', edit_player, methods=['POST']),
    Route('/api/registry/players/{id:int}', view_player),
    Route('/api/registry/players', list_players)
]