from starlette.requests import Request
from starlette.routing import Route
from api.auth import require_permission
from api.data import handle
from api.utils.responses import JSONResponse, bind_request_body
from common.auth import permissions
from common.data.commands import ImportMKCV1DataCommand
from common.data.models import MKCV1Data

@bind_request_body(MKCV1Data)
@require_permission(permissions.IMPORT_V1_DATA)
async def import_data(request: Request, body: MKCV1Data):
    await handle(ImportMKCV1DataCommand(body))
    return JSONResponse({}, status_code=200)

routes = [
    Route('/api/mkcv1/import', import_data, methods=["POST"])
]