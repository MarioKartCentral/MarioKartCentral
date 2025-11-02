from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route
from api import appsettings
from api.auth import require_logged_in, require_permission, get_user_info
from common.auth import permissions
from api.data import handle
from api.utils.responses import JSONResponse, bind_request_body
from api.utils.word_filter import check_word_filter
from common.data.commands import *
from common.data.models import Problem, EditUserSettingsRequestData
from datetime import timedelta

@require_logged_in()
async def get_settings(request: Request) -> Response:
    command = GetUserSettingsCommand(request.state.user.id)
    user_settings = await handle(command)
    if user_settings is None:
        raise Problem("User settings not found", status=404)

    return JSONResponse(user_settings)

@bind_request_body(EditUserSettingsRequestData)
@check_word_filter
@require_permission(permissions.EDIT_PROFILE, check_denied_only=True)
async def edit_settings(request: Request, body: EditUserSettingsRequestData) -> JSONResponse:
    command = EditUserSettingsCommand(request.state.user.id, body)
    succeeded = await handle(command)
    if not succeeded:
        raise Problem("User not found", status=400)
    resp = JSONResponse({}, status_code=200)

    # set language and color_scheme cookies
    if body.language is not None:
        resp.set_cookie('language', body.language, secure=appsettings.SECURE_HTTP_COOKIES, httponly=True, max_age=int(timedelta(days=365).total_seconds()))
    if body.color_scheme is not None:
        resp.set_cookie('color_scheme', body.color_scheme, secure=appsettings.SECURE_HTTP_COOKIES, httponly=True)

    return resp

@bind_request_body(EditPlayerUserSettingsRequestData)
@check_word_filter
@require_permission(permissions.EDIT_PLAYER)
async def edit_player_user_settings(request: Request, body: EditPlayerUserSettingsRequestData) -> JSONResponse:
    command = EditPlayerUserSettingsCommand(body)
    await handle(command)
    return JSONResponse({})
    
@bind_request_body(SetLanguageRequestData)
@get_user_info
async def edit_language(request: Request, body: SetLanguageRequestData) -> JSONResponse:
    resp = JSONResponse({}, status_code=200)
    resp.set_cookie('language', body.language, secure=appsettings.SECURE_HTTP_COOKIES, httponly=True, max_age=int(timedelta(days=365).total_seconds()))
    if request.state.user:
        command_body = EditUserSettingsRequestData(language=body.language)
        command = EditUserSettingsCommand(request.state.user.id, command_body)
        await handle(command)
    return resp

routes = [
    Route('/api/user/settings', get_settings),
    Route('/api/user/settings/edit', edit_settings, methods=["POST"]),
    Route('/api/user/settings/forceEdit', edit_player_user_settings, methods=["POST"]),
    Route('/api/user/settings/editLanguage', edit_language, methods=["POST"]),
]