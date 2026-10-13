from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from api.auth import inject_current_user, require_logged_in
from api.data import State
from api.utils.responses import JSONResponse, bind_request_body, bind_request_query
from common.data.commands import *
from common.data.models import MarkAsReadRequestData, NotificationFilter


@bind_request_query(NotificationFilter)
@require_logged_in()
@inject_current_user
async def list_notifications(request: Request[State], user: User, body: NotificationFilter) -> JSONResponse:
    command = GetNotificationsCommand(user.id, body)
    notifications = await request.state.command_handler.handle(command)
    return JSONResponse(notifications, headers={"Cache-Control": "private, max-age=60", "Vary": "Cookie"})


@bind_request_body(MarkAsReadRequestData)
@require_logged_in()
@inject_current_user
async def edit_single_read_status(request: Request[State], user: User, body: MarkAsReadRequestData) -> JSONResponse:
    command = MarkOneNotificationAsReadCommand(
        request.path_params['id'], user.id, body)
    count = await request.state.command_handler.handle(command)
    return JSONResponse({"count": count})


@bind_request_body(MarkAsReadRequestData)
@require_logged_in()
@inject_current_user
async def edit_all_read_status(request: Request[State], user: User, body: MarkAsReadRequestData) -> JSONResponse:
    command = MarkAllNotificationsAsReadCommand(user.id, body)
    count = await request.state.command_handler.handle(command)
    return JSONResponse({'update_count': count})


@require_logged_in()
@inject_current_user
async def get_unread_count(request: Request[State], user: User) -> JSONResponse:
    command = GetUnreadNotificationsCountCommand(user.id)
    count = await request.state.command_handler.handle(command)
    return JSONResponse({'count': count})

routes = [
    Route('/api/notifications/list', list_notifications),
    Route('/api/notifications/edit/read_status/{id:int}',
          edit_single_read_status, methods=["POST"]),
    Route('/api/notifications/edit/read_status/all',
          edit_all_read_status, methods=["POST"]),
    Route('/api/notifications/unread_count', get_unread_count)
]
