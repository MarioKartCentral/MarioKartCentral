from starlette.requests import Request
from starlette.routing import Route
from api.auth import require_permission, require_tournament_permission, require_series_permission
from api.data import handle
from api.utils.responses import JSONResponse, bind_request_body, bind_request_query
from common.auth import permissions, series_permissions, tournament_permissions
from common.data.commands import *
from common.data.models import *

@bind_request_body(CreateTournamentRequestData)
@require_series_permission(series_permissions.CREATE_TOURNAMENT)
async def create_tournament(request: Request, body: CreateTournamentRequestData) -> JSONResponse:
    command = CreateTournamentCommand(body)
    await handle(command)
    return JSONResponse({})

@bind_request_body(EditTournamentRequestData)
@require_tournament_permission(tournament_permissions.EDIT_TOURNAMENT)
async def edit_tournament(request: Request, body: EditTournamentRequestData) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    command = EditTournamentCommand(body, tournament_id)
    await handle(command)
    return JSONResponse({})

async def tournament_info(request: Request) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
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

@bind_request_body(EditSeriesRequestData)
@require_series_permission(series_permissions.EDIT_SERIES)
async def edit_series(request: Request, body: EditSeriesRequestData) -> JSONResponse:
    series_id = request.path_params['series_id']
    command = EditSeriesCommand(body, series_id)
    await handle(command)
    return JSONResponse({})

async def series_info(request: Request) -> JSONResponse:
    series_id = request.path_params['series_id']
    command = GetSeriesDataCommand(series_id)
    series = await handle(command)
    return JSONResponse(series)

@bind_request_query(SeriesFilter)
async def series_list(request: Request, filter: SeriesFilter) -> JSONResponse:
    command = GetSeriesListCommand(filter)
    series = await handle(command)
    return JSONResponse(series)

@bind_request_body(TournamentTemplateRequestData)
@require_series_permission(series_permissions.CREATE_TOURNAMENT_TEMPLATE)
async def create_template(request: Request, body: TournamentTemplateRequestData) -> JSONResponse:
    command = CreateTournamentTemplateCommand(body)
    await handle(command)
    return JSONResponse({})

@bind_request_body(TournamentTemplateRequestData)
@require_series_permission(series_permissions.EDIT_TOURNAMENT_TEMPLATE)
async def edit_template(request: Request, body: TournamentTemplateRequestData) -> JSONResponse:
    template_id = request.path_params['template_id']
    command = EditTournamentTemplateCommand(body, template_id)
    await handle(command)
    return JSONResponse({})

async def template_info(request: Request) -> JSONResponse:
    template_id = request.path_params['template_id']
    command = GetTournamentTemplateDataCommand(template_id)
    template = await handle(command)
    return JSONResponse(template)

@bind_request_query(TemplateFilter)
async def template_list(request: Request, filter: TemplateFilter) -> JSONResponse:
    command = GetTournamentTemplateListCommand(filter)
    templates = await handle(command)
    return JSONResponse(templates)

routes = [
    Route('/api/tournaments/create', create_tournament, methods=["POST"]),
    Route('/api/tournaments/{tournament_id:int}/edit', edit_tournament, methods=["POST"]),
    Route('/api/tournaments/{tournament_id:int}', tournament_info),
    Route('/api/tournaments/list', tournament_list),
    Route('/api/tournaments/series/create', create_series, methods=['POST']),
    Route('/api/tournaments/series/{series_id:int}/edit', edit_series, methods=['POST']),
    Route('/api/tournaments/series/{series_id:int}', series_info),
    Route('/api/tournaments/series/list', series_list),
    Route('/api/tournaments/templates/create', create_template, methods=['POST']),
    Route('/api/tournaments/templates/{template_id:int}/edit', edit_template, methods=['POST']),
    Route('/api/tournaments/templates/{template_id:int}', template_info),
    Route('/api/tournaments/templates/list', template_list)    
]