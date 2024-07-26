from starlette.requests import Request
from starlette.routing import Route
from api.auth import require_permission, require_logged_in, require_tournament_permission
from api.data import handle
from api.utils.responses import JSONResponse, bind_request_body, bind_request_query
from common.auth import permissions, series_permissions, tournament_permissions
from common.data.commands import *
from common.data.models import *

# endpoint used when a user creates their own squad
@bind_request_body(CreateSquadRequestData)
@require_tournament_permission(tournament_permissions.REGISTER_TOURNAMENT, check_denied_only=True)
#@require_logged_in
async def create_my_squad(request: Request, body: CreateSquadRequestData) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    player_id = request.state.user.player_id
    command = CreateSquadCommand(body.squad_name, body.squad_tag, body.squad_color, player_id, player_id, tournament_id, 
        False, body.mii_name, body.can_host, body.selected_fc_id, [], [], admin=False)
    await handle(command)
    return JSONResponse({})

# endpoint used when a non-moderator user registers a team for a tournament
@bind_request_body(RegisterTeamRequestData)
@require_tournament_permission(tournament_permissions.REGISTER_TOURNAMENT, check_denied_only=True)
async def register_my_team(request: Request, body: RegisterTeamRequestData) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    player_id = request.state.user.player_id
    command = CreateSquadCommand(body.squad_name, body.squad_tag, body.squad_color, player_id, body.captain_player, tournament_id,
                                 False, None, False, None, body.roster_ids, body.representative_ids, admin=False)
    await handle(command)
    return JSONResponse({})

@bind_request_body(RegisterTeamRequestData)
@require_tournament_permission(tournament_permissions.MANAGE_TOURNAMENT_REGISTRATIONS)
async def force_register_team(request: Request, body: RegisterTeamRequestData) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    command = CreateSquadCommand(body.squad_name, body.squad_tag, body.squad_color, body.captain_player, body.captain_player, tournament_id,
                                 False, None, False, None, body.roster_ids, body.representative_ids, admin=True)
    await handle(command)
    return JSONResponse({})

# endpoint used when a tournament staff creates a squad with another user in it
@bind_request_body(ForceCreateSquadRequestData)
@require_tournament_permission(tournament_permissions.MANAGE_TOURNAMENT_REGISTRATIONS)
async def force_create_squad(request: Request, body: ForceCreateSquadRequestData) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    command = CreateSquadCommand(body.squad_name, body.squad_tag, body.squad_color, body.player_id, body.player_id, tournament_id, 
        False, body.mii_name, body.can_host, body.selected_fc_id, body.roster_ids, body.representative_ids, admin=True)
    await handle(command)
    return JSONResponse({})

@bind_request_body(EditSquadRequestData)
@require_tournament_permission(tournament_permissions.MANAGE_TOURNAMENT_REGISTRATIONS)
async def edit_squad(request: Request, body: EditSquadRequestData) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    command = EditSquadCommand(tournament_id, body.squad_id, body.squad_name, body.squad_tag, body.squad_color, body.is_registered)
    await handle(command)
    return JSONResponse({})

@bind_request_body(EditMySquadRequestData)
@require_tournament_permission(tournament_permissions.REGISTER_TOURNAMENT, check_denied_only=True)
async def edit_my_squad(request: Request, body: EditMySquadRequestData) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    captain_player_id = request.state.user.player_id
    command = CheckSquadCaptainPermissionsCommand(tournament_id, body.squad_id, captain_player_id)
    await handle(command)
    command = EditSquadCommand(tournament_id, body.squad_id, body.squad_name, body.squad_tag, body.squad_color, True)
    await handle(command)
    return JSONResponse({})

# used when the captain of a squad invites a player to their squad.
# use force_register_player in tournament staff contexts
@bind_request_body(InvitePlayerRequestData)
@require_tournament_permission(tournament_permissions.REGISTER_TOURNAMENT, check_denied_only=True)
async def invite_player(request: Request, body: InvitePlayerRequestData) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    captain_player_id = request.state.user.player_id
    command = CheckSquadCaptainPermissionsCommand(tournament_id, body.squad_id, captain_player_id)
    await handle(command)
    command = RegisterPlayerCommand(body.player_id, tournament_id, body.squad_id, False, False, None, False, True, None, body.is_representative, False)
    await handle(command)
    return JSONResponse({})

# endpoint used when a user registers themself for a tournament
@bind_request_body(RegisterPlayerRequestData)
@require_tournament_permission(tournament_permissions.REGISTER_TOURNAMENT, check_denied_only=True)
async def register_me(request: Request, body: RegisterPlayerRequestData) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    player_id = request.state.user.player_id
    command = RegisterPlayerCommand(player_id, tournament_id, None, False, False, body.mii_name, body.can_host, False, body.selected_fc_id, False, False)
    await handle(command)
    return JSONResponse({})

# endpoint used when a tournament staff registers another player for a tournament (requires permissions)
@bind_request_body(ForceRegisterPlayerRequestData)
@require_tournament_permission(tournament_permissions.MANAGE_TOURNAMENT_REGISTRATIONS)
async def force_register_player(request: Request, body: ForceRegisterPlayerRequestData) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    command = RegisterPlayerCommand(body.player_id, tournament_id, body.squad_id, body.is_squad_captain, body.is_checked_in, 
        body.mii_name, body.can_host, body.is_invite, body.selected_fc_id, body.is_representative,True)
    await handle(command)
    return JSONResponse({})

@bind_request_body(EditPlayerRegistrationRequestData)
@require_tournament_permission(tournament_permissions.MANAGE_TOURNAMENT_REGISTRATIONS)
async def edit_registration(request: Request, body: EditPlayerRegistrationRequestData) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    command = EditPlayerRegistrationCommand(tournament_id, body.squad_id, body.player_id, body.mii_name, body.can_host,
        body.is_invite, body.is_checked_in, body.is_squad_captain, body.selected_fc_id, body.is_representative, True)
    await handle(command)
    return JSONResponse({})

@bind_request_body(EditMyRegistrationRequestData)
@require_tournament_permission(tournament_permissions.REGISTER_TOURNAMENT, check_denied_only=True)
async def edit_my_registration(request: Request, body: EditMyRegistrationRequestData) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    player_id = request.state.user.player_id
    command = EditPlayerRegistrationCommand(tournament_id, body.squad_id, player_id, body.mii_name, body.can_host, False, None, None, body.selected_fc_id,
                                            None, False)
    await handle(command)
    return JSONResponse({})

@bind_request_body(AcceptInviteRequestData)
@require_tournament_permission(tournament_permissions.REGISTER_TOURNAMENT, check_denied_only=True)
async def accept_invite(request: Request, body: AcceptInviteRequestData) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    player_id = request.state.user.player_id
    command = EditPlayerRegistrationCommand(tournament_id, body.squad_id, player_id, body.mii_name, body.can_host,
        False, False, False, body.selected_fc_id, None, False)
    await handle(command)
    return JSONResponse({})

@bind_request_body(DeclineInviteRequestData)
@require_logged_in
async def decline_invite(request: Request, body: DeclineInviteRequestData) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    player_id = request.state.user.player_id
    command = UnregisterPlayerCommand(tournament_id, body.squad_id, player_id, False)
    await handle(command)
    return JSONResponse({})

# used when a squad captain wants to remove a member from their squad
@bind_request_body(KickSquadPlayerRequestData)
@require_tournament_permission(tournament_permissions.REGISTER_TOURNAMENT, check_denied_only=True)
async def remove_player_from_squad(request: Request, body: KickSquadPlayerRequestData) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    captain_player_id = request.state.user.player_id
    command = CheckSquadCaptainPermissionsCommand(tournament_id, body.squad_id, captain_player_id)
    await handle(command)
    command = UnregisterPlayerCommand(tournament_id, body.squad_id, body.player_id, False)
    await handle(command)
    return JSONResponse({})

# used when a player unregisters themself from the tournament
@bind_request_body(UnregisterPlayerRequestData)
@require_logged_in
async def unregister_me(request: Request, body: UnregisterPlayerRequestData) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    player_id = request.state.user.player_id
    command = UnregisterPlayerCommand(tournament_id, body.squad_id, player_id, False)
    await handle(command)
    return JSONResponse({})

# used when a staff member force removes a player from the tournament
@bind_request_body(StaffUnregisterPlayerRequestData)
@require_tournament_permission(tournament_permissions.MANAGE_TOURNAMENT_REGISTRATIONS)
async def staff_unregister(request: Request, body: StaffUnregisterPlayerRequestData) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    command = UnregisterPlayerCommand(tournament_id, body.squad_id, body.player_id, True)
    await handle(command)
    return JSONResponse({})

@bind_request_body(MakeCaptainRequestData)
@require_tournament_permission(tournament_permissions.REGISTER_TOURNAMENT, check_denied_only=True)
async def change_squad_captain(request: Request, body: MakeCaptainRequestData) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    captain_player_id = request.state.user.player_id
    command = CheckSquadCaptainPermissionsCommand(tournament_id, body.squad_id, captain_player_id)
    await handle(command)
    command = ChangeSquadCaptainCommand(tournament_id, body.squad_id, body.player_id)
    await handle(command)
    return JSONResponse({})

@bind_request_body(UnregisterSquadRequestData)
@require_logged_in
async def unregister_squad(request: Request, body: UnregisterSquadRequestData) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    captain_player_id = request.state.user.player_id
    command = CheckSquadCaptainPermissionsCommand(tournament_id, body.squad_id, captain_player_id)
    await handle(command)
    command = UnregisterSquadCommand(tournament_id, body.squad_id)
    await handle(command)
    return JSONResponse({})

async def view_squad(request: Request) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    squad_id = request.path_params['squad_id']
    command = GetSquadDetailsCommand(tournament_id, squad_id)
    squad = await handle(command)
    return JSONResponse(squad)

@bind_request_query(TournamentRegistrationFilter)
async def list_registrations(request: Request, body: TournamentRegistrationFilter) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    command = CheckIfSquadTournament(tournament_id)
    is_squad = await handle(command)
    if is_squad:
        command = GetSquadRegistrationsCommand(tournament_id, body.registered_only, body.eligible_only, body.hosts_only)
    else:
        command = GetFFARegistrationsCommand(tournament_id, body.hosts_only)
    registrations = await handle(command)
    return JSONResponse(registrations)

@require_logged_in
async def my_registration(request: Request) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    player_id = request.state.user.player_id
    if not player_id:
        return JSONResponse(None)
    command = CheckIfSquadTournament(tournament_id)
    is_squad = await handle(command)
    
    if is_squad:
        command = GetPlayerSquadRegCommand(tournament_id, request.state.user.player_id)
    else:
        command = GetPlayerSoloRegCommand(tournament_id, request.state.user.player_id)
    registrations = await handle(command)
    return JSONResponse(registrations)

routes = [
    Route('/api/tournaments/{tournament_id:int}/register', register_me, methods=['POST']),
    Route('/api/tournaments/{tournament_id:int}/forceRegister', force_register_player, methods=['POST']),
    Route('/api/tournaments/{tournament_id:int}/editRegistration', edit_registration, methods=['POST']),
    Route('/api/tournaments/{tournament_id:int}/editMyRegistration', edit_my_registration, methods=['POST']),
    Route('/api/tournaments/{tournament_id:int}/createSquad', create_my_squad, methods=['POST']),
    Route('/api/tournaments/{tournament_id:int}/registerTeam', register_my_team, methods=['POST']),
    Route('/api/tournaments/{tournament_id:int}/forceRegisterTeam', force_register_team, methods=['POST']),
    Route('/api/tournaments/{tournament_id:int}/forceCreateSquad', force_create_squad, methods=['POST']),
    Route('/api/tournaments/{tournament_id:int}/editSquad', edit_squad, methods=['POST']),
    Route('/api/tournaments/{tournament_id:int}/editMySquad', edit_my_squad, methods=['POST']),
    Route('/api/tournaments/{tournament_id:int}/invitePlayer', invite_player, methods=['POST']),
    Route('/api/tournaments/{tournament_id:int}/acceptInvite', accept_invite, methods=['POST']),
    Route('/api/tournaments/{tournament_id:int}/declineInvite', decline_invite, methods=['POST']),
    Route('/api/tournaments/{tournament_id:int}/kickPlayer', remove_player_from_squad, methods=['POST']),
    Route('/api/tournaments/{tournament_id:int}/unregister', unregister_me, methods=['POST']),
    Route('/api/tournaments/{tournament_id:int}/forceUnregister', staff_unregister, methods=['POST']),
    Route('/api/tournaments/{tournament_id:int}/makeCaptain', change_squad_captain, methods=['POST']),
    Route('/api/tournaments/{tournament_id:int}/unregisterSquad', unregister_squad, methods=['POST']),
    Route('/api/tournaments/{tournament_id:int}/squads/{squad_id:int}', view_squad),
    Route('/api/tournaments/{tournament_id:int}/registrations', list_registrations),
    Route('/api/tournaments/{tournament_id:int}/myRegistration', my_registration)
]