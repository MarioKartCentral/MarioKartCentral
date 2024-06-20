from starlette.requests import Request
from starlette.routing import Route
from api.auth import require_permission
from api.data import handle
from api.utils.responses import JSONResponse, bind_request_body, bind_request_query
from common.auth import permissions
from common.data.commands import *
from common.data.models import *

@bind_request_body(CreateTournamentRequestData)
@require_permission(permissions.CREATE_TOURNAMENT)
async def create_tournament(request: Request, body: CreateTournamentRequestData) -> JSONResponse:
    command = CreateTournamentCommand(body)
    await handle(command)
    return JSONResponse({})

@bind_request_body(EditTournamentRequestData)
@require_permission(permissions.EDIT_TOURNAMENT)
async def edit_tournament(request: Request, body: EditTournamentRequestData) -> JSONResponse:
    tournament_id = request.path_params['id']
    command = EditTournamentCommand(body, tournament_id)
    await handle(command)
    return JSONResponse({})

async def tournament_info(request: Request) -> JSONResponse:
    tournament_id = request.path_params['id']
    command = GetTournamentDataCommand(tournament_id)
    tournament = await handle(command)
    return JSONResponse(tournament)

@bind_request_query(TournamentFilter)
async def tournament_list(request: Request, filter: TournamentFilter) -> JSONResponse:
    command = GetTournamentListCommand(filter)
    tournaments = await handle(command)
    return JSONResponse(tournaments)

@bind_request_body(SeriesRequestData)
@require_permission(permissions.CREATE_SERIES)
async def create_series(request: Request, body: SeriesRequestData) -> JSONResponse:
    command = CreateSeriesCommand(body)
    await handle(command)
    return JSONResponse({})

@bind_request_body(SeriesRequestData)
@require_permission(permissions.EDIT_SERIES)
async def edit_series(request: Request, body: SeriesRequestData) -> JSONResponse:
    series_id = request.path_params['id']
    command = EditSeriesCommand(body, series_id)
    await handle(command)
    return JSONResponse({})

async def series_info(request: Request) -> JSONResponse:
    series_id = request.path_params['id']
    command = GetSeriesDataCommand(series_id)
    series = await handle(command)
    return JSONResponse(series)

@bind_request_query(SeriesFilter)
async def series_list(request: Request, filter: SeriesFilter) -> JSONResponse:
    command = GetSeriesListCommand(filter)
    series = await handle(command)
    return JSONResponse(series)

@bind_request_body(TournamentTemplateRequestData)
@require_permission(permissions.CREATE_TOURNAMENT_TEMPLATE)
async def create_template(request: Request, body: TournamentTemplateRequestData) -> JSONResponse:
    command = CreateTournamentTemplateCommand(body)
    await handle(command)
    return JSONResponse({})

@bind_request_body(TournamentTemplateRequestData)
@require_permission(permissions.EDIT_TOURNAMENT_TEMPLATE)
async def edit_template(request: Request, body: TournamentTemplateRequestData) -> JSONResponse:
    template_id = request.path_params['id']
    command = EditTournamentTemplateCommand(body, template_id)
    await handle(command)
    return JSONResponse({})

async def template_info(request: Request) -> JSONResponse:
    template_id = request.path_params['id']
    command = GetTournamentTemplateDataCommand(template_id)
    template = await handle(command)
    return JSONResponse(template)

@bind_request_query(TemplateFilter)
async def template_list(request: Request, filter: TemplateFilter) -> JSONResponse:
    command = GetTournamentTemplateListCommand(filter)
    templates = await handle(command)
    return JSONResponse(templates)

async def series_placements(request: Request) -> JSONResponse:
    tournament_id = request.path_params['id']
    command = GetTournamentListWithTop3(tournament_id)
    series = await handle(command)
    return JSONResponse(series)

routes = [
    Route('/api/tournaments/create', create_tournament, methods=["POST"]),
    Route('/api/tournaments/{id:int}/edit', edit_tournament, methods=["POST"]),
    Route('/api/tournaments/{id:int}', tournament_info),
    Route('/api/tournaments/list', tournament_list),
    Route('/api/tournaments/series/create', create_series, methods=['POST']),
    Route('/api/tournaments/series/{id:int}/edit', edit_series, methods=['POST']),
    Route('/api/tournaments/series/{id:int}', series_info),
    Route('/api/tournaments/series/list', series_list),
    Route('/api/tournaments/templates/create', create_template, methods=['POST']),
    Route('/api/tournaments/templates/{id:int}/edit', edit_template, methods=['POST']),
    Route('/api/tournaments/templates/{id:int}', template_info),
    Route('/api/tournaments/templates/list', template_list),
    Route('/api/tournaments/series/{id:int}/placements', series_placements)
]