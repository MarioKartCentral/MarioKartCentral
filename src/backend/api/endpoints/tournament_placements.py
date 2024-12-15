from starlette.requests import Request
from starlette.routing import Route
from api.data import handle
from api.utils.responses import JSONResponse, bind_request_body
from api.auth import require_tournament_permission, check_tournament_visiblity
from common.auth import tournament_permissions
from common.data.commands import *
from common.data.models import *

@bind_request_body(list[TournamentPlacement])
@require_tournament_permission(tournament_permissions.MANAGE_PLACEMENTS)
async def set_placements(request: Request, body: list[TournamentPlacement]) -> JSONResponse:
    tournament_id = int(request.path_params['tournament_id'])
    command = CheckIfSquadTournament(tournament_id)
    is_squad = await handle(command)
    if is_squad:
        reg_command = GetSquadRegistrationsCommand(tournament_id, True, True, False, True)
        registrations = await handle(reg_command)
    else:
        reg_command = GetFFARegistrationsCommand(tournament_id, True, False, True)
        registrations = await handle(reg_command)

    placements_command = SetPlacementsCommand(tournament_id, is_squad, body, registrations)
    await handle(placements_command)

    return JSONResponse({})

@check_tournament_visiblity
async def get_placements(request: Request) -> JSONResponse:
    tournament_id = int(request.path_params['tournament_id'])
    command = CheckIfSquadTournament(tournament_id)
    is_squad = await handle(command)
    if is_squad:
        reg_command = GetSquadRegistrationsCommand(tournament_id, True, True, False, True)
        squads = await handle(reg_command)
        placements_command = GetSquadPlacementsCommand(tournament_id, squads)
        placements = await handle(placements_command)
    else:
        reg_command = GetFFARegistrationsCommand(tournament_id, True, False, True)
        players = await handle(reg_command)
        placements_command = GetSoloPlacementsCommand(tournament_id, players)
        placements = await handle(placements_command)

    return JSONResponse(placements)

<<<<<<< HEAD
<<<<<<< HEAD
=======
=======
>>>>>>> 24fce649a92f23cd2ce182d6f51d67c1c8e0b090
async def get_player_placements(request: Request) -> JSONResponse:
    player_id = int(request.path_params['player_id'])
    placements_command = GetPlayerTournamentPlacementsCommand(player_id)
    placements = await handle(placements_command)
    return JSONResponse(placements)

async def get_team_placements(request: Request) -> JSONResponse:
    team_id = int(request.path_params['team_id'])
    command = GetTeamTournamentPlacementsCommand(team_id)
    placements = await handle(command)
    return JSONResponse(placements)


<<<<<<< HEAD
>>>>>>> 31ea3e1 (intermediate push)
=======
>>>>>>> 24fce649a92f23cd2ce182d6f51d67c1c8e0b090
routes = [
    Route('/api/tournaments/{tournament_id:int}/placements/set', set_placements, methods=["POST"]),
    Route('/api/tournaments/{tournament_id:int}/placements', get_placements),
    Route('/api/tournaments/players/placements/{player_id:int}', get_player_placements),
    Route('/api/tournaments/teams/placements/{team_id:int}', get_team_placements)
]
