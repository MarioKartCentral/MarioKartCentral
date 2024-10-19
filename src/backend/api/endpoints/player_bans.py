from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route
from api.auth import require_permission
from api.data import handle
from api.utils.responses import JSONResponse, bind_request_body, bind_request_query
from common.auth import permissions
from common.data.commands import *
from common.data.models import *
from common.auth.roles import BANNED
import common.data.notifications as notifications

@bind_request_body(PlayerBanRequestData)
@require_permission(permissions.BAN_PLAYER)
async def ban_player(request: Request, body: PlayerBanRequestData) -> Response:
    player_id = request.path_params['id']
    banned_by_id = request.state.user.id
    expires_on = None if body.is_indefinite else body.expiration_date
    await handle(GrantRoleCommand(banned_by_id, player_id, BANNED, expires_on, True))
    player_ban = await handle(BanPlayerCommand(player_id, banned_by_id, body))
    user_id = await handle(GetUserIdFromPlayerIdCommand(player_id))
    unban_date_text = 'Indefinite' if body.is_indefinite else f'DATE-{body.expiration_date}'
    await handle(DispatchNotificationCommand([user_id], notifications.BANNED , [body.reason, unban_date_text], f'/registry/players/profile?id={player_id}', notifications.CRITICAL))
    return JSONResponse(player_ban, status_code=200)

@require_permission(permissions.BAN_PLAYER)
async def unban_player(request: Request) -> Response:
    player_id = request.path_params['id']
    unbanned_by_id = request.state.user.id
    await handle(RemoveRoleCommand(unbanned_by_id, player_id, BANNED, True))
    player_unban = await handle(UnbanPlayerCommand(player_id, unbanned_by_id))
    user_id = await handle(GetUserIdFromPlayerIdCommand(player_id))
    await handle(DispatchNotificationCommand([user_id], notifications.UNBANNED, [], f'/registry/players/profile?id={player_id}', notifications.INFO))
    return JSONResponse(player_unban, status_code=200)

@bind_request_body(PlayerBanRequestData)
@require_permission(permissions.BAN_PLAYER)
async def edit_player_ban(request: Request, body: PlayerBanRequestData) -> Response:
    player_id = request.path_params['id']
    banned_by_id = request.state.user.id
    expires_on = None if body.is_indefinite else body.expiration_date

    await handle(UpdateRoleExpirationCommand(banned_by_id, player_id, BANNED, expires_on))
    player_ban = await handle(EditPlayerBanCommand(player_id, banned_by_id, body))
    return JSONResponse(player_ban, status_code=200)

@bind_request_query(PlayerBanFilter)
@require_permission(permissions.BAN_PLAYER)
async def list_banned_players(request: Request, filter: PlayerBanFilter) -> Response:
    command = ListBannedPlayersCommand(filter)
    bans = await handle(command)
    return JSONResponse(bans, status_code=200)

@bind_request_query(PlayerBanHistoricalFilter)
@require_permission(permissions.BAN_PLAYER)
async def list_banned_players_historical(request: Request, filter: PlayerBanHistoricalFilter) -> Response:
    command = ListBannedPlayersHistoricalCommand(filter)
    bans = await handle(command)
    return JSONResponse(bans, status_code=200)

routes = [
    Route('/api/registry/players/{id:int}/ban', ban_player, methods=['POST']), # dispatches notification
    Route('/api/registry/players/{id:int}/editBan', edit_player_ban, methods=['POST']),
    Route('/api/registry/players/{id:int}/ban', unban_player, methods=['DELETE']), # dispatches notification
    Route('/api/registry/players/bans', list_banned_players),
    Route('/api/registry/players/historicalBans', list_banned_players_historical)
]