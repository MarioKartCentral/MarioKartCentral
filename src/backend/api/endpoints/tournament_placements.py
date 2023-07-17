from starlette.requests import Request
from starlette.routing import Route
from api.auth import require_permission
from api.data import handle
from api.utils.responses import JSONResponse, bind_request_body, bind_request_query
from common.auth import permissions
from common.data.commands import *
from common.data.models import *

@bind_request_body(List[Placements])
async def set_placements(request: Request, body: List[Placements]) -> JSONResponse:
    tournament_id = request.path_params['id']
    command = SetPlacementsCommand(tournament_id, body)
    await handle(command)
    return JSONResponse({})


async def get_placements(request: Request) -> JSONResponse:
    tournament_id = request.path_params['id']
    command = CheckIfSquadTournament(tournament_id)
    is_squad = await handle(command)
    command = GetPlacementsCommand(tournament_id, is_squad)
    placements = await handle(command)
    return JSONResponse(placements)



routes = [
    Route('/api/tournaments/{id:int}/placements/set', set_placements, methods=["POST"]),
    Route('/api/tournaments/{id:int}/placements', get_placements)
]