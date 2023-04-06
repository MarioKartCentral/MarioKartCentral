from dataclasses import dataclass
from starlette.requests import Request
from starlette.routing import Route
from api.auth import require_permission, require_logged_in
from api.data import connect_db, handle
from api.utils.responses import JSONResponse, bind_request_body
from common.auth import permissions
from common.data.commands import (CreateSquadCommand, GetPlayerIdForUserCommand, RegisterPlayerCommand, EditSquadCommand, CheckSquadCaptainPermissionsCommand,
    EditPlayerRegistrationCommand, UnregisterPlayerCommand, GetSquadDetailsCommand)
from common.data.models import (CreateSquadRequestData, ForceCreateSquadRequestData, EditSquadRequestData, InvitePlayerRequestData,
    RegisterPlayerRequestData, ForceRegisterPlayerRequestData, EditPlayerRegistrationRequestData, AcceptInviteRequestData,
    DeclineInviteRequestData, UnregisterPlayerRequestData, StaffUnregisterPlayerRequestData)

# endpoint used when a user creates their own squad
@bind_request_body(CreateSquadRequestData)
@require_logged_in
async def create_my_squad(request: Request, body: CreateSquadRequestData) -> JSONResponse:
    tournament_id = request.path_params['id']
    user_id = request.state.user.id
    player_id = await handle(GetPlayerIdForUserCommand(user_id))
    command = CreateSquadCommand(body.squad_name, body.squad_tag, body.squad_color, player_id, tournament_id, False, body.mii_name, body.can_host)
    await handle(command)
    return JSONResponse({})

# endpoint used when a tournament staff creates a squad with another user in it
@bind_request_body(ForceCreateSquadRequestData)
@require_permission(permissions.MANAGE_TOURNAMENT_REGISTRATIONS)
async def force_create_squad(request: Request, body: ForceCreateSquadRequestData) -> JSONResponse:
    tournament_id = request.path_params['id']
    command = CreateSquadCommand(body.squad_name, body.squad_tag, body.squad_color, body.player_id, tournament_id, False, body.mii_name, body.can_host)
    await handle(command)
    return JSONResponse({})

@bind_request_body(EditSquadRequestData)
async def edit_squad(request: Request, body: EditSquadRequestData) -> JSONResponse:
    tournament_id = request.path_params['id']
    command = EditSquadCommand(tournament_id, body.squad_id, body.squad_name, body.squad_tag, body.squad_color, body.is_registered)
    await handle(command)
    return JSONResponse({})

# used when the captain of a squad invites a player to their squad.
# use force_register_player in tournament staff contexts
@require_logged_in
@bind_request_body(InvitePlayerRequestData)
async def invite_player(request: Request, body: InvitePlayerRequestData) -> JSONResponse:
    tournament_id = request.path_params['id']
    captain_player_id = request.state.user.player_id
    command = CheckSquadCaptainPermissionsCommand(tournament_id, body.squad_id, captain_player_id)
    await handle(command)
    command = RegisterPlayerCommand(body.player_id, tournament_id, body.squad_id, False, False, None, False, True, False)
    await handle(command)
    return JSONResponse({})

# endpoint used when a user registers themself for a tournament
@require_logged_in
@bind_request_body(RegisterPlayerRequestData)
async def register_me(request: Request, body: RegisterPlayerRequestData) -> JSONResponse:
    tournament_id = request.path_params['id']
    player_id = request.state.user.player_id
    command = RegisterPlayerCommand(player_id, tournament_id, None, False, False, body.mii_name, body.can_host, False, False)
    await handle(command)
    return JSONResponse({})

# endpoint used when a tournament staff registers another player for a tournament (requires permissions)
@require_permission(permissions.MANAGE_TOURNAMENT_REGISTRATIONS)
@bind_request_body(ForceRegisterPlayerRequestData)
async def force_register_player(request: Request, body: ForceRegisterPlayerRequestData) -> JSONResponse:
    tournament_id = request.path_params['id']
    command = RegisterPlayerCommand(body.player_id, tournament_id, body.squad_id, body.is_squad_captain, body.is_checked_in, 
        body.mii_name, body.can_host, body.is_invite, True)
    await handle(command)
    return JSONResponse({})

@require_permission(permissions.MANAGE_TOURNAMENT_REGISTRATIONS)
@bind_request_body(EditPlayerRegistrationRequestData)
async def edit_registration(request: Request, body: EditPlayerRegistrationRequestData) -> JSONResponse:
    tournament_id = request.path_params['id']
    command = EditPlayerRegistrationCommand(tournament_id, body.squad_id, body.player_id, body.mii_name, body.can_host,
        body.is_invite, body.is_checked_in, body.is_squad_captain, True)
    await handle(command)
    return JSONResponse({})

@require_logged_in
@bind_request_body(AcceptInviteRequestData)
async def accept_invite(request: Request, body: AcceptInviteRequestData) -> JSONResponse:
    tournament_id = request.path_params['id']
    player_id = request.state.user.player_id
    command = EditPlayerRegistrationCommand(tournament_id, body.squad_id, player_id, body.mii_name, body.can_host,
        False, False, False, False)
    await handle(command)
    return JSONResponse({})

@require_logged_in
@bind_request_body(DeclineInviteRequestData)
async def decline_invite(request: Request, body: DeclineInviteRequestData) -> JSONResponse:
    tournament_id = request.path_params['id']
    player_id = request.state.user.player_id
    command = UnregisterPlayerCommand(tournament_id, body.squad_id, player_id, False)
    await handle(command)
    return JSONResponse({})

async def unregister_player(tournament_id, player_id, squad_id=None):
    is_invite = 0
    async with connect_db() as db:
        async with db.execute("DELETE FROM tournament_players WHERE tournament_id = ? AND player_id = ? AND squad_id = ? AND is_invite = ?", (tournament_id, player_id, squad_id, is_invite)) as cursor:
            edited_rows = cursor.rowcount
            if edited_rows == 0:
                return JSONResponse({'error': 'Player not found in tournament'}, status_code=400)
    return JSONResponse({'success': 'Successfully unregistered player'}, status_code=201)

@require_logged_in
@bind_request_body(InvitePlayerRequestData)
# used when a squad captain wants to remove a member from their squad
async def remove_player_from_squad(request: Request, body: InvitePlayerRequestData) -> JSONResponse:
    tournament_id = request.path_params['id']
    captain_player_id = request.state.user.player_id
    command = CheckSquadCaptainPermissionsCommand(tournament_id, body.squad_id, captain_player_id)
    await handle(command)
    command = UnregisterPlayerCommand(tournament_id, body.squad_id, body.player_id, False)
    await handle(command)
    return JSONResponse({})

# used when a player unregisters themself from the tournament
@require_logged_in
@bind_request_body(UnregisterPlayerRequestData)
async def unregister_me(request: Request, body: UnregisterPlayerRequestData) -> JSONResponse:
    tournament_id = request.path_params['id']
    player_id = request.state.user.player_id
    command = UnregisterPlayerCommand(tournament_id, body.squad_id, player_id, False)
    await handle(command)
    return JSONResponse({})

# used when a staff member force removes a player from the tournament
@require_permission(permissions.MANAGE_TOURNAMENT_REGISTRATIONS)
@bind_request_body(StaffUnregisterPlayerRequestData)
async def staff_unregister(request: Request, body: StaffUnregisterPlayerRequestData) -> JSONResponse:
    tournament_id = request.path_params['id']
    command = UnregisterPlayerCommand(tournament_id, body.squad_id, body.player_id, True)
    await handle(command)
    return JSONResponse({})

async def view_squad(request: Request) -> JSONResponse:
    tournament_id = request.path_params['id']
    squad_id = request.path_params['squad_id']
    command = GetSquadDetailsCommand(tournament_id, squad_id)
    squad = await handle(command)
    return JSONResponse(squad)

async def squad_registrations(tournament_id, eligible_only):
    where_clause = ""
    if eligible_only:
        where_clause = "AND is_registered = 1"
    async with connect_db() as db:
        async with db.execute(f"SELECT id, name, tag, color, timestamp, is_registered FROM tournament_squads WHERE tournament_id = ? {where_clause}", (tournament_id,)) as cursor:
            rows = await cursor.fetchall()
            squads = {}
            for row in rows:
                squad_id = int(row[0])
                curr_squad = {
                    'id': squad_id,
                    'name': row[1],
                    'tag': row[2],
                    'color': row[3],
                    'timestamp': row[4],
                    'is_registered': row[5],
                    'players': []
                }
                squads[squad_id] = curr_squad
        async with db.execute(f"SELECT id, player_id, squad_id, is_squad_captain, timestamp, is_checked_in, mii_name, can_host, is_invite FROM tournament_players WHERE tournament_id = ?", (tournament_id,)) as cursor:
            rows = await cursor.fetchall()
            for row in rows:
                squad_id = int(row[2])
                if squad_id not in squads:
                    continue
                curr_player = {
                    'id': row[0],
                    'player_id': row[1],
                    'is_squad_captain': row[3],
                    'timestamp': row[4],
                    'is_checked_in': row[5],
                    'mii_name': row[6],
                    'can_host': row[7],
                    'is_invite': row[8]
                }
                squads[squad_id]['players'].append(curr_player)
    return JSONResponse({'squads': [s for s in squads.values()]})
            

async def ffa_registrations(tournament_id):
    async with connect_db() as db:
        async with db.execute("SELECT id, player_id, timestamp, is_checked_in, mii_name, can_host FROM tournament_players WHERE tournament_id = ?", (tournament_id,)) as cursor:
            rows = await cursor.fetchall()
            players = []
            for row in rows:
                curr_player = {
                    'id': row[0],
                    'player_id': row[1],
                    'timestamp': row[2],
                    'is_checked_in': row[3],
                    'mii_name': row[4],
                    'can_host': row[5],
                }
                players.append(curr_player)
    return JSONResponse({'players': players})


async def list_registrations(request: Request) -> JSONResponse:
    tournament_id = request.path_params['id']
    eligible_only = False
    if "eligibleOnly" in request.query_params:
        eligible_only = True
    async with connect_db() as db:
        async with db.execute("SELECT is_squad FROM tournaments WHERE id = ?", (tournament_id,)) as cursor:
            row = await cursor.fetchone()
            if row is None:
                return JSONResponse({'error': 'Tournament not found'}, status_code=404)
            is_squad = row[0]
    if is_squad == 1:
        return await squad_registrations(tournament_id, eligible_only)
    return await ffa_registrations(tournament_id)

routes = [
    Route('/api/tournaments/{id:int}/register', register_me, methods=['POST']),
    Route('/api/tournaments/{id:int}/forceRegister', force_register_player, methods=['POST']),
    Route('/api/tournaments/{id:int}/editRegistration', edit_registration, methods=['POST']),
    Route('/api/tournaments/{id:int}/createSquad', create_my_squad, methods=['POST']),
    Route('/api/tournaments/{id:int}/forceCreateSquad', force_create_squad, methods=['POST']),
    Route('/api/tournaments/{id:int}/editSquad', edit_squad, methods=['POST']),
    Route('/api/tournaments/{id:int}/invitePlayer', invite_player, methods=['POST']),
    Route('/api/tournaments/{id:int}/acceptInvite', accept_invite, methods=['POST']),
    Route('/api/tournaments/{id:int}/declineInvite', decline_invite, methods=['POST']),
    Route('/api/tournaments/{id:int}/kickPlayer', remove_player_from_squad, methods=['POST']),
    Route('/api/tournaments/{id:int}/unregister', unregister_me, methods=['POST']),
    Route('/api/tournaments/{id:int}/forceUnregister', staff_unregister, methods=['POST']),
    Route('/api/tournaments/{id:int}/squads/{squad_id:int}', view_squad),
    Route('/api/tournaments/{id:int}/registrations', list_registrations)
]