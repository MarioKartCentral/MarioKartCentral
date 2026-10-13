from starlette.requests import Request
from starlette.routing import Route
from api.data import State
from api.auth import require_permission
from api.utils.responses import Response
from common.data.models import *
from common.data.commands import *
from common.auth import permissions


@require_permission(permissions.CREATE_DB_BACKUPS)
async def create_db_backup(request: Request[State]) -> Response:
    await request.state.command_handler.handle(BackupDatabasesCommand())
    return Response(status_code=204)

routes: list[Route] = [
    Route('/api/admin/db_backup', create_db_backup, methods=["POST"]),
]
