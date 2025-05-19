from starlette.requests import Request
from starlette.routing import Route
from api.auth import require_permission
from api.utils.responses import JSONResponse
from api.data import handle
from common.data.models import *
from common.data.commands import *
from common.auth import permissions

@require_permission(permissions.CREATE_DB_BACKUPS)
async def create_db_backup(request: Request) -> JSONResponse:
    await handle(BackupDatabasesCommand())
    return JSONResponse({})

routes: list[Route] = [
    Route('/api/admin/db_backup', create_db_backup, methods=["POST"]),
]