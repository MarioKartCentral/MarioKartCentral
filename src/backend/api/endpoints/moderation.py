from starlette.requests import Request
from starlette.routing import Route
from api.auth import require_permission
from api.data import handle
from api.utils.responses import JSONResponse, bind_request_body, bind_request_query
from common.data.models import FilteredWords, FriendCodeEditFilter
from common.data.commands import *
from common.auth import permissions

@bind_request_body(FilteredWords)
@require_permission(permissions.MANAGE_WORD_FILTER)
async def edit_word_filter(request: Request, words: FilteredWords) -> JSONResponse:
    await handle(EditWordFilterCommand(words))
    return JSONResponse({})

@require_permission(permissions.MANAGE_WORD_FILTER)
async def view_word_filter(request: Request) -> JSONResponse:
    word_filter = await handle(GetWordFilterCommand())
    return JSONResponse(word_filter)

@bind_request_query(FriendCodeEditFilter)
@require_permission(permissions.EDIT_PLAYER)
async def list_friend_code_edits(request: Request, filter: FriendCodeEditFilter) -> JSONResponse:
    edits = await handle(ListFriendCodeEditsCommand(filter))
    return JSONResponse(edits)

@bind_request_query(AltFlagFilter)
@require_permission(permissions.VIEW_ALT_FLAGS)
async def list_alt_flags(request: Request, filter: AltFlagFilter) -> JSONResponse:
    flags = await handle(ListAltFlagsCommand(filter))
    return JSONResponse(flags)

@bind_request_query(PlayerAltFlagRequestData)
@require_permission(permissions.VIEW_ALT_FLAGS)
async def view_player_alt_flags(request: Request, body: PlayerAltFlagRequestData) -> JSONResponse:
    flags = await handle(ViewPlayerAltFlagsCommand(body.player_id))
    return JSONResponse(flags)

@require_permission(permissions.VIEW_USER_LOGINS)
async def view_player_user_logins(request: Request) -> JSONResponse:
    player_id = request.path_params['player_id']
    # check if the user has permissions to view actual ip addresses
    has_ip_permission = await handle(CheckUserHasPermissionCommand(request.state.user.id, permissions.VIEW_IP_ADDRESSES))
    player_logins = await handle(ViewPlayerLoginHistoryCommand(player_id, has_ip_permission))
    return JSONResponse(player_logins)

@require_permission(permissions.VIEW_BASIC_IP_INFO)
async def view_player_ip_history(request: Request) -> JSONResponse:
    player_id = request.path_params['player_id']
    # check if the user has permissions to view actual ip addresses
    has_ip_permission = await handle(CheckUserHasPermissionCommand(request.state.user.id, permissions.VIEW_IP_ADDRESSES))
    player_ips = await handle(ViewPlayerIPHistoryCommand(player_id, has_ip_permission))
    return JSONResponse(player_ips)

@require_permission(permissions.VIEW_BASIC_IP_INFO)
async def view_ip_history(request: Request) -> JSONResponse:
    ip_id = request.path_params['ip_id']
    # check if the user has permissions to view actual ip addresses
    has_ip_permission = await handle(CheckUserHasPermissionCommand(request.state.user.id, permissions.VIEW_IP_ADDRESSES))
    ip_history = await handle(ViewHistoryForIPCommand(ip_id, has_ip_permission))
    return JSONResponse(ip_history)

@require_permission(permissions.VIEW_IP_ADDRESSES)
async def view_ip_history_from_address(request: Request) -> JSONResponse:
    ip_address = request.path_params['ip_address']
    ip_id = await handle(GetIPIDFromAddressCommand(ip_address))
    ip_history = await handle(ViewHistoryForIPCommand(ip_id, True))
    return JSONResponse(ip_history)

@require_permission(permissions.VIEW_FINGERPRINTS)
async def view_fingerprint(request: Request) -> JSONResponse:
    fingerprint_hash = request.path_params['fingerprint_hash']
    fingerprint = await handle(GetFingerprintDataCommand(fingerprint_hash))
    return JSONResponse(fingerprint)

routes: list[Route] = [
    Route('/api/moderator/wordFilter/edit', edit_word_filter, methods=['POST']),
    Route('/api/moderator/wordFilter', view_word_filter),
    Route('/api/moderator/friendCodeEdits', list_friend_code_edits),
    Route('/api/moderator/altFlags', list_alt_flags),
    Route('/api/moderator/playerAltFlags', view_player_alt_flags),
    Route('/api/moderator/player_logins/{player_id:int}', view_player_user_logins),
    Route('/api/moderator/player_ips/{player_id:int}', view_player_ip_history),
    Route('/api/moderator/ip_addresses/{ip_id:int}', view_ip_history),
    Route('/api/moderator/ip_addresses/from_address/{ip_address:str}', view_ip_history_from_address),
    Route('/api/moderator/fingerprints/{fingerprint_hash:str}', view_fingerprint),
]