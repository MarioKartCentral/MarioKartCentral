from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route
from api.auth import require_permission
from api.data import handle
from api.utils.responses import JSONResponse, bind_request_body, bind_request_query
from common.auth import permissions
from common.data.commands import *
from common.data.models import *

@bind_request_body(PlayerBanRequestData)
@require_permission(permissions.BAN_PLAYER)
async def ban_player(request: Request, body: PlayerBanRequestData) -> Response:
    command = BanPlayerCommand(request.path_params['id'], request.state.user.id, body)
    player_ban = await handle(command)
    return JSONResponse(player_ban, status_code=200)

@require_permission(permissions.BAN_PLAYER)
async def unban_player(request: Request) -> Response:
    command = UnbanPlayerCommand(request.path_params['id'])
    await handle(command)
    return JSONResponse({}, status_code=200)

@bind_request_body(PlayerBanRequestData)
@require_permission(permissions.BAN_PLAYER)
async def edit_player_ban(request: Request, body: PlayerBanRequestData) -> Response:
    command = EditPlayerBanCommand(request.path_params['id'], request.state.user.id, body)
    player_ban = await handle(command)
    return JSONResponse(player_ban, status_code=200)

@bind_request_query(PlayerBanFilter)
@require_permission(permissions.BAN_PLAYER)
async def list_banned_players(request: Request, filter: PlayerBanFilter) -> Response:
    command = ListBannedPlayersCommand(filter)
    bans = await handle(command)
    return JSONResponse(bans, status_code=200)

routes = [
    Route('/api/registry/players/{id:int}/ban', ban_player, methods=['POST']),
    Route('/api/registry/players/{id:int}/editBan', edit_player_ban, methods=['POST']),
    Route('/api/registry/players/{id:int}/unban', unban_player, methods=['POST']),
    Route('/api/registry/players/bans', list_banned_players)
]