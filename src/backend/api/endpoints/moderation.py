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

routes: list[Route] = [
    Route('/api/moderator/wordFilter/edit', edit_word_filter, methods=['POST']),
    Route('/api/moderator/wordFilter', view_word_filter),
    Route('/api/moderator/friendCodeEdits', list_friend_code_edits),
    Route('/api/moderator/altFlags', list_alt_flags),
    Route('/api/moderator/playerAltFlags', view_player_alt_flags),
]