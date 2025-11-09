from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route
from starlette.background import BackgroundTask
from api.auth import require_permission
from api.data import handle
from api.utils.responses import JSONResponse, bind_request_body, bind_request_query
from common.auth import permissions, roles as user_roles
from common.data import notifications
from common.data.commands import *
from common.data.models import *

@bind_request_body(PlayerBanRequestData)
@require_permission(permissions.BAN_PLAYER)
async def ban_player(request: Request, body: PlayerBanRequestData) -> Response:
    async def notify():
        if user_id is None:
            return
        unban_date_text = 'Indefinite' if body.is_indefinite else f'DATE-{body.expiration_date}'
        content_args = {'reason': body.reason, 'date': unban_date_text}
        await handle(DispatchNotificationCommand([user_id], notifications.BANNED , content_args, f'/registry/players/profile?id={player_id}', notifications.CRITICAL))

    player_id = request.path_params['id']
    banned_by_id = request.state.user.id
    expires_on = None if body.is_indefinite else body.expiration_date
    user_id = await handle(GetUserIdFromPlayerIdCommand(player_id))
    if user_id is not None:
        await handle(GrantRoleCommand(banned_by_id, player_id, user_roles.BANNED, expires_on, True))
    player_ban = await handle(BanPlayerCommand(player_id, banned_by_id, body))
    return JSONResponse(player_ban, status_code=200, background=BackgroundTask(notify))


@require_permission(permissions.BAN_PLAYER)
async def unban_player(request: Request) -> Response:
    async def notify():
        if user_id is None:
            return
        await handle(DispatchNotificationCommand([user_id], notifications.UNBANNED, {}, f'/registry/players/profile?id={player_id}', notifications.INFO))

    player_id = request.path_params['id']
    unbanned_by_id = request.state.user.id
    user_id = await handle(GetUserIdFromPlayerIdCommand(player_id))
    if user_id is not None:
        await handle(RemoveRoleCommand(unbanned_by_id, player_id, user_roles.BANNED, True))
    player_unban = await handle(UnbanPlayerCommand(player_id, unbanned_by_id))
    return JSONResponse(player_unban, status_code=200, background=BackgroundTask(notify))

@bind_request_body(PlayerBanRequestData)
@require_permission(permissions.BAN_PLAYER)
async def edit_player_ban(request: Request, body: PlayerBanRequestData) -> Response:
    async def notify():
        # No notification is sent if only the comment section is updated
        if ban_list.ban_list:
            cur_ban = ban_list.ban_list[0]
            if cur_ban.reason != body.reason or cur_ban.is_indefinite != body.is_indefinite or cur_ban.expiration_date != body.expiration_date:
                unban_date_text = 'Indefinite' if body.is_indefinite else f'DATE-{body.expiration_date}'
                
                if user_id is None:
                    return
                content_args = {'reason': body.reason, 'date': unban_date_text}
                await handle(DispatchNotificationCommand([user_id], notifications.BAN_CHANGE, content_args, f'/registry/players/profile?id={player_id}', notifications.WARNING))

    player_id = request.path_params['id']
    banned_by_id = request.state.user.id
    expires_on = None if body.is_indefinite else body.expiration_date
    ban_list = await handle(ListBannedPlayersCommand(PlayerBanFilter(player_id=player_id)))
    user_id = await handle(GetUserIdFromPlayerIdCommand(player_id))
    if user_id is not None:
        await handle(UpdateRoleExpirationCommand(banned_by_id, player_id, user_roles.BANNED, expires_on, is_ban=True))
    player_ban = await handle(EditPlayerBanCommand(player_id, banned_by_id, body))        
    return JSONResponse(player_ban, status_code=200, background=BackgroundTask(notify))

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
    Route('/api/registry/players/{id:int}/editBan', edit_player_ban, methods=['POST']), # dispatches notification
    Route('/api/registry/players/{id:int}/ban', unban_player, methods=['DELETE']), # dispatches notification
    Route('/api/registry/players/bans', list_banned_players),
    Route('/api/registry/players/historicalBans', list_banned_players_historical)
]