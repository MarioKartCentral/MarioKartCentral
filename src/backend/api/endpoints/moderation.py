from starlette.requests import Request
from starlette.routing import Route
from api.auth import inject_current_user, require_permission
from api.data import State
from api.utils.responses import JSONResponse, bind_request_body, bind_request_query
from common.data.models import FilteredWords, FriendCodeEditFilter
from common.data.commands import *
from common.auth import permissions


@bind_request_body(FilteredWords)
@require_permission(permissions.MANAGE_WORD_FILTER)
async def edit_word_filter(request: Request[State], words: FilteredWords) -> JSONResponse:
    await request.state.command_handler.handle(EditWordFilterCommand(words))
    return JSONResponse({})


@require_permission(permissions.MANAGE_WORD_FILTER)
async def view_word_filter(request: Request[State]) -> JSONResponse:
    word_filter = await request.state.command_handler.handle(GetWordFilterCommand())
    return JSONResponse(word_filter)


@bind_request_query(FriendCodeEditFilter)
@require_permission(permissions.EDIT_PLAYER)
async def list_friend_code_edits(request: Request[State], filter: FriendCodeEditFilter) -> JSONResponse:
    edits = await request.state.command_handler.handle(ListFriendCodeEditsCommand(filter))
    return JSONResponse(edits)


@bind_request_query(AltFlagFilter)
@require_permission(permissions.VIEW_ALT_FLAGS)
async def list_alt_flags(request: Request[State], filter: AltFlagFilter) -> JSONResponse:
    flags = await request.state.command_handler.handle(ListAltFlagsCommand(filter))
    return JSONResponse(flags)


@bind_request_query(PlayerAltFlagRequestData)
@require_permission(permissions.VIEW_ALT_FLAGS)
async def view_player_alt_flags(request: Request[State], body: PlayerAltFlagRequestData) -> JSONResponse:
    flags = await request.state.command_handler.handle(ViewPlayerAltFlagsCommand(body.player_id, body.exclude_fingerprints))
    return JSONResponse(flags)


@require_permission(permissions.VIEW_USER_LOGINS)
@inject_current_user
async def view_player_user_logins(request: Request[State], user: User) -> JSONResponse:
    player_id = request.path_params['player_id']
    # check if the user has permissions to view actual ip addresses
    has_ip_permission = await request.state.command_handler.handle(CheckUserHasPermissionCommand(user.id, permissions.VIEW_IP_ADDRESSES))
    player_logins = await request.state.command_handler.handle(ViewPlayerLoginHistoryCommand(player_id, has_ip_permission))
    return JSONResponse(player_logins)


@require_permission(permissions.VIEW_BASIC_IP_INFO)
@inject_current_user
async def view_player_ip_history(request: Request[State], user: User) -> JSONResponse:
    player_id = request.path_params['player_id']
    # check if the user has permissions to view actual ip addresses
    has_ip_permission = await request.state.command_handler.handle(CheckUserHasPermissionCommand(user.id, permissions.VIEW_IP_ADDRESSES))
    player_ips = await request.state.command_handler.handle(ViewPlayerIPHistoryCommand(player_id, has_ip_permission))
    return JSONResponse(player_ips)


@require_permission(permissions.VIEW_BASIC_IP_INFO)
@inject_current_user
async def view_ip_history(request: Request[State], user: User) -> JSONResponse:
    ip_id = request.path_params['ip_id']
    # check if the user has permissions to view actual ip addresses
    has_ip_permission = await request.state.command_handler.handle(CheckUserHasPermissionCommand(user.id, permissions.VIEW_IP_ADDRESSES))
    ip_history = await request.state.command_handler.handle(ViewHistoryForIPCommand(ip_id, has_ip_permission))
    return JSONResponse(ip_history)


@bind_request_query(IPFilter)
@require_permission(permissions.VIEW_BASIC_IP_INFO)
@inject_current_user
async def search_ip_addresses(request: Request[State], user: User, body: IPFilter) -> JSONResponse:
    # check if the user has permissions to view actual ip addresses
    has_ip_permission = await request.state.command_handler.handle(CheckUserHasPermissionCommand(user.id, permissions.VIEW_IP_ADDRESSES))
    results = await request.state.command_handler.handle(SearchIPsCommand(body, has_ip_permission))
    return JSONResponse(results)


@require_permission(permissions.VIEW_FINGERPRINTS)
async def view_fingerprint(request: Request[State]) -> JSONResponse:
    fingerprint_hash = request.path_params['fingerprint_hash']
    fingerprint = await request.state.command_handler.handle(GetFingerprintDataCommand(fingerprint_hash))
    return JSONResponse(fingerprint)

routes: list[Route] = [
    Route('/api/moderator/wordFilter/edit',
          edit_word_filter, methods=['POST']),
    Route('/api/moderator/wordFilter', view_word_filter),
    Route('/api/moderator/friendCodeEdits', list_friend_code_edits),
    Route('/api/moderator/altFlags', list_alt_flags),
    Route('/api/moderator/playerAltFlags', view_player_alt_flags),
    Route(
        '/api/moderator/player_logins/{player_id:int}', view_player_user_logins),
    Route('/api/moderator/player_ips/{player_id:int}', view_player_ip_history),
    Route('/api/moderator/ip_addresses/{ip_id:int}', view_ip_history),
    Route('/api/moderator/ip_addresses', search_ip_addresses),
    Route(
        '/api/moderator/fingerprints/{fingerprint_hash:str}', view_fingerprint),
]
