from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route
from api import appsettings
from api.auth import inject_current_user, require_logged_in, require_permission, get_user_info
from api.data import State
from common.auth import permissions
from api.utils.responses import JSONResponse, bind_request_body
from api.utils.word_filter import check_word_filter
from common.data.commands import *
from common.data.models import Problem, EditUserSettingsRequestData
from datetime import timedelta


@require_logged_in()
@inject_current_user
async def get_settings(request: Request[State], user: User) -> Response:
    command = GetUserSettingsCommand(user.id)
    user_settings = await request.state.command_handler.handle(command)
    if user_settings is None:
        raise Problem("User settings not found", status=404)

    return JSONResponse(user_settings)


@bind_request_body(EditUserSettingsRequestData)
@check_word_filter
@require_permission(permissions.EDIT_PROFILE, check_denied_only=True)
@inject_current_user
async def edit_settings(request: Request[State], user: User, body: EditUserSettingsRequestData) -> JSONResponse:
    command = EditUserSettingsCommand(user.id, body)
    succeeded = await request.state.command_handler.handle(command)
    if not succeeded:
        raise Problem("User not found", status=400)
    resp = JSONResponse({}, status_code=200)

    # set language and color_scheme cookies
    if body.language is not None:
        resp.set_cookie('language', body.language, secure=appsettings.SECURE_HTTP_COOKIES,
                        httponly=True, max_age=int(timedelta(days=365).total_seconds()))
    if body.color_scheme is not None:
        resp.set_cookie('color_scheme', body.color_scheme,
                        secure=appsettings.SECURE_HTTP_COOKIES, httponly=True)

    return resp


@bind_request_body(EditPlayerUserSettingsRequestData)
@check_word_filter
@require_permission(permissions.EDIT_PLAYER)
async def edit_player_user_settings(request: Request[State], body: EditPlayerUserSettingsRequestData) -> JSONResponse:
    command = EditPlayerUserSettingsCommand(body)
    await request.state.command_handler.handle(command)
    return JSONResponse({})


@bind_request_body(SetLanguageRequestData)
@get_user_info
async def edit_language(request: Request[State], body: SetLanguageRequestData) -> JSONResponse:
    resp = JSONResponse({}, status_code=200)
    resp.set_cookie('language', body.language, secure=appsettings.SECURE_HTTP_COOKIES,
                    httponly=True, max_age=int(timedelta(days=365).total_seconds()))

    user = request.state.user
    if user:
        command_body = EditUserSettingsRequestData(language=body.language)
        command = EditUserSettingsCommand(user.id, command_body)
        await request.state.command_handler.handle(command)
    return resp

routes = [
    Route('/api/user/settings', get_settings),
    Route('/api/user/settings/edit', edit_settings, methods=["POST"]),
    Route('/api/user/settings/forceEdit',
          edit_player_user_settings, methods=["POST"]),
    Route('/api/user/settings/editLanguage', edit_language, methods=["POST"]),
]
