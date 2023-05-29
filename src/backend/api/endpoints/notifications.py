from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from api.auth import require_logged_in
from api.data import handle
from api.utils.responses import JSONResponse, bind_request_body, bind_request_query
from common.data.commands import *
from common.data.models import MarkAsReadRequestData, NotificationFilter

@bind_request_query(NotificationFilter)
@require_logged_in
async def list_notifications(request: Request, body: NotificationFilter) -> JSONResponse:
    command = GetNotificationsCommand(request.state.user.id, body)
    notifications = await handle(command)
    return JSONResponse(notifications)

@bind_request_body(MarkAsReadRequestData)
@require_logged_in
async def edit_single_read_status(request: Request, body: MarkAsReadRequestData) -> JSONResponse:
    command = MarkOneNotificationAsReadCommand(request.path_params['id'], request.state.user.id, body)
    count = await handle(command)
    return JSONResponse({"count": count})

@bind_request_body(MarkAsReadRequestData)
@require_logged_in
async def edit_all_read_status(request: Request, body: MarkAsReadRequestData) -> JSONResponse:
    command = MarkAllNotificationsAsReadCommand(request.state.user.id, body)
    count = await handle(command)
    return JSONResponse({'update_count': count})

@require_logged_in
async def get_unread_count(request: Request) -> JSONResponse:
    command = GetUnreadNotificationsCountCommand(request.state.user.id)
    count = await handle(command)
    return JSONResponse({'count': count})

routes = [
    Route('/api/notifications/list', list_notifications),
    Route('/api/notifications/edit/read_status/{id:int}', edit_single_read_status, methods=["POST"]),
    Route('/api/notifications/edit/read_status/all', edit_all_read_status, methods=["POST"]),
    Route('/api/notifications/unread_count', get_unread_count)
]