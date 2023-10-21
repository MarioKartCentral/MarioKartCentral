from starlette.requests import Request
from starlette.routing import Route
from api.auth import require_logged_in
from api.data import handle
from api.utils.responses import JSONResponse, bind_request_body, bind_request_query
from common.data.commands import *
from common.data.models import Record

@bind_request_body(Record)
@require_logged_in
async def submit_record(request: Request, body: Record) -> JSONResponse:
    # todo: permissions
    command = SubmitRecordCommand(body)
    await handle(command)
    return JSONResponse({})

@bind_request_body(Record)
@require_logged_in
async def update_record(request: Request, body: Record) -> JSONResponse:
    # todo: permissions
    command = UpdateRecordCommand(body)
    await handle(command)
    return JSONResponse({})

async def get_record(request: Request) -> JSONResponse:
    record_id = request.path_params['id']
    command = GetRecordData(record_id)
    record_data = await handle(command)
    return JSONResponse(record_data)

async def get_records_for_player(request: Request) -> JSONResponse:
    player_id = request.path_params['player_id']
    command = GetRecordsForPlayer(player_id)
    records = await handle(command)
    return JSONResponse(records)

@bind_request_query(RecordCategory)
async def get_records_for_category(request: Request, category: RecordCategory) -> JSONResponse:
    command = GetRecordsForCategory(category)
    records = await handle(command)
    return JSONResponse(records)

routes = [
    Route('/api/records/create', submit_record, methods=["POST"]),
    Route('/api/records/edit', update_record, methods=["POST"]),
    Route('/api/records/{id:int}', get_record, methods=["GET"]),
    Route('/api/records/player/{player_id:int}', get_records_for_player, methods=["GET"]),
    Route('/api/records/category', get_records_for_category, methods=["GET"])
]