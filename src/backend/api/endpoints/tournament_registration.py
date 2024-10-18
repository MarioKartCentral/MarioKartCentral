from starlette.requests import Request
from starlette.routing import Route
from api.auth import require_logged_in, require_tournament_permission
from api.data import handle
from api.utils.responses import JSONResponse, bind_request_body, bind_request_query
from common.auth import tournament_permissions
from common.data.commands import *
from common.data.models import *
import common.data.notifications as notifications

# endpoint used when a user creates their own squad
@bind_request_body(CreateSquadRequestData)
@require_tournament_permission(tournament_permissions.REGISTER_TOURNAMENT, check_denied_only=True)
async def create_my_squad(request: Request, body: CreateSquadRequestData) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    player_id = request.state.user.player_id
    player_host_permission = await handle(CheckUserHasPermissionCommand(request.state.user.id, tournament_permissions.REGISTER_HOST, True, 
                                                                        tournament_id=tournament_id))
    if body.can_host and not player_host_permission:
        raise Problem("User does not have permission to register as a host", status=401)
    command = CreateSquadCommand(body.squad_name, body.squad_tag, body.squad_color, player_id, tournament_id, 
        False, body.is_bagger_clause, body.mii_name, body.can_host, body.selected_fc_id, False, is_privileged=False)
    await handle(command)
    return JSONResponse({})

# endpoint used when a non-moderator user registers a team for a tournament
@bind_request_body(RegisterTeamRequestData)
@require_tournament_permission(tournament_permissions.REGISTER_TOURNAMENT, check_denied_only=True)
async def register_my_team(request: Request, body: RegisterTeamRequestData) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    player_id = request.state.user.player_id
    command = RegisterTeamTournamentCommand(tournament_id, body.squad_name, body.squad_tag, body.squad_color,
                                            player_id, body.roster_ids, body.players, False)
    await handle(command)
    return JSONResponse({})

@bind_request_body(RegisterTeamRequestData)
@require_tournament_permission(tournament_permissions.MANAGE_TOURNAMENT_REGISTRATIONS)
async def force_register_team(request: Request, body: RegisterTeamRequestData) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    player_id = request.state.user.player_id
    command = RegisterTeamTournamentCommand(tournament_id, body.squad_name, body.squad_tag, body.squad_color,
                                            player_id, body.roster_ids, body.players, True, is_privileged=True)
    
    squad_id = await handle(command)
    if squad_id:
        data = await handle(GetNotificationSquadDataCommand(tournament_id, squad_id))
        await handle(DispatchNotificationCommand([data.captain_user_id], notifications.STAFF_REGISTER_TEAM, [data.tournament_name], f'/tournaments/details?id={tournament_id}', notifications.SUCCESS))
    return JSONResponse({})

# endpoint used when a tournament staff creates a squad with another user in it
@bind_request_body(ForceCreateSquadRequestData)
@require_tournament_permission(tournament_permissions.MANAGE_TOURNAMENT_REGISTRATIONS)
async def force_create_squad(request: Request, body: ForceCreateSquadRequestData) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    command = CreateSquadCommand(body.squad_name, body.squad_tag, body.squad_color, body.player_id, tournament_id, 
        body.is_checked_in, body.is_bagger_clause, body.mii_name, body.can_host, body.selected_fc_id, body.is_approved, is_privileged=True)
    await handle(command)

    tournament_name = await handle(GetTournamentNameFromIdCommand(tournament_id))
    user_id = await handle(GetUserIdFromPlayerIdCommand(body.player_id))
    await handle(DispatchNotificationCommand([user_id], notifications.STAFF_CREATE_SQUAD, [tournament_name], f'/tournaments/details?id={tournament_id}', notifications.INFO))
    return JSONResponse({})

@bind_request_body(EditSquadRequestData)
@require_tournament_permission(tournament_permissions.MANAGE_TOURNAMENT_REGISTRATIONS)
async def edit_squad(request: Request, body: EditSquadRequestData) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    command = EditSquadCommand(tournament_id, body.squad_id, body.squad_name, body.squad_tag, body.squad_color, body.is_registered, body.is_approved)
    await handle(command)
    return JSONResponse({})

@bind_request_body(EditMySquadRequestData)
@require_tournament_permission(tournament_permissions.REGISTER_TOURNAMENT, check_denied_only=True)
async def edit_my_squad(request: Request, body: EditMySquadRequestData) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    captain_player_id = request.state.user.player_id
    command = CheckSquadCaptainPermissionsCommand(tournament_id, body.squad_id, captain_player_id)
    await handle(command)
    command = EditSquadCommand(tournament_id, body.squad_id, body.squad_name, body.squad_tag, body.squad_color, True, None)
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
    command = RegisterPlayerCommand(body.player_id, tournament_id, body.squad_id, False, False, None, False, True, None, body.is_representative, body.is_bagger_clause, False, False)
    await handle(command)
    user_id = await handle(GetUserIdFromPlayerIdCommand(body.player_id))
    data = await handle(GetNotificationSquadDataCommand(tournament_id, body.squad_id))
    await handle(DispatchNotificationCommand([user_id], notifications.TOURNAMENT_INVITE , [data.squad_name or '', data.tournament_name], '/registry/invites', notifications.SUCCESS))
    return JSONResponse({})

# endpoint used when a user registers themself for a tournament
@bind_request_body(RegisterPlayerRequestData)
@require_tournament_permission(tournament_permissions.REGISTER_TOURNAMENT, check_denied_only=True)
async def register_me(request: Request, body: RegisterPlayerRequestData) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    player_id = request.state.user.player_id
    player_host_permission = await handle(CheckUserHasPermissionCommand(request.state.user.id, tournament_permissions.REGISTER_HOST, True, 
                                                                        tournament_id=tournament_id))
    if body.can_host and not player_host_permission:
        raise Problem("User does not have permission to register as a host", status=401)
    command = RegisterPlayerCommand(player_id, tournament_id, None, False, False, body.mii_name, body.can_host, False, body.selected_fc_id, False, False, False, False)
    await handle(command)
    return JSONResponse({})

# endpoint used when a tournament staff registers another player for a tournament (requires permissions)
@bind_request_body(ForceRegisterPlayerRequestData)
@require_tournament_permission(tournament_permissions.MANAGE_TOURNAMENT_REGISTRATIONS)
async def force_register_player(request: Request, body: ForceRegisterPlayerRequestData) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    command = RegisterPlayerCommand(body.player_id, tournament_id, body.squad_id, body.is_squad_captain, body.is_checked_in, 
        body.mii_name, body.can_host, body.is_invite, body.selected_fc_id, body.is_representative, body.is_bagger_clause, body.is_approved, True)
    await handle(command)

    user_id = await handle(GetUserIdFromPlayerIdCommand(body.player_id))
    player_name = await handle(GetPlayerNameCommand(body.player_id))
    if body.squad_id:
        data = await handle(GetNotificationSquadDataCommand(tournament_id, body.squad_id))
        await handle(DispatchNotificationCommand([data.captain_user_id], notifications.TOURNAMENT_STAFF_REGISTERED_CAPTAIN_NOTIF , [player_name, data.tournament_name], f'/tournaments/details?id={tournament_id}', notifications.INFO))
        await handle(DispatchNotificationCommand([user_id], notifications.TOURNAMENT_STAFF_REGISTERED , [data.tournament_name], f'/tournaments/details?id={tournament_id}', notifications.SUCCESS))
    return JSONResponse({})

@bind_request_body(EditPlayerRegistrationRequestData)
@require_tournament_permission(tournament_permissions.MANAGE_TOURNAMENT_REGISTRATIONS)
async def edit_registration(request: Request, body: EditPlayerRegistrationRequestData) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    command = EditPlayerRegistrationCommand(tournament_id, body.squad_id, body.player_id, body.mii_name, body.can_host,
        body.is_invite, body.is_checked_in, body.is_squad_captain, body.selected_fc_id, body.is_representative, 
        body.is_bagger_clause, body.is_approved, True)
    await handle(command)

    tournament_name = await handle(GetTournamentNameFromIdCommand(tournament_id))
    user_id = await handle(GetUserIdFromPlayerIdCommand(body.player_id))
    await handle(DispatchNotificationCommand([user_id], notifications.STAFF_EDIT_PLAYER_REGISTRATION , [tournament_name], f'/tournaments/details?id={tournament_id}', notifications.INFO))
    return JSONResponse({})

@bind_request_body(EditMyRegistrationRequestData)
@require_tournament_permission(tournament_permissions.REGISTER_TOURNAMENT, check_denied_only=True)
async def edit_my_registration(request: Request, body: EditMyRegistrationRequestData) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    player_id = request.state.user.player_id
    player_host_permission = await handle(CheckUserHasPermissionCommand(request.state.user.id, tournament_permissions.REGISTER_HOST, True, 
                                                                        tournament_id=tournament_id))
    if body.can_host and not player_host_permission:
        raise Problem("User does not have permission to register as a host", status=401)
    command = EditPlayerRegistrationCommand(tournament_id, body.squad_id, player_id, body.mii_name, body.can_host, False, None, None, body.selected_fc_id,
                                            None, None, None, False)
    await handle(command)
    return JSONResponse({})

@bind_request_body(AcceptInviteRequestData)
@require_tournament_permission(tournament_permissions.REGISTER_TOURNAMENT, check_denied_only=True)
async def accept_invite(request: Request, body: AcceptInviteRequestData) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    player_id = request.state.user.player_id
    player_host_permission = await handle(CheckUserHasPermissionCommand(request.state.user.id, tournament_permissions.REGISTER_HOST, True, 
                                                                        tournament_id=tournament_id))
    if body.can_host and not player_host_permission:
        raise Problem("User does not have permission to register as a host", status=401)
    
    player_name = await handle(GetPlayerNameCommand(player_id))
    data = await handle(GetNotificationSquadDataCommand(tournament_id, body.squad_id))
    command = EditPlayerRegistrationCommand(tournament_id, body.squad_id, player_id, body.mii_name, body.can_host,
        False, False, False, body.selected_fc_id, None, None, None, False)
    await handle(command)
    await handle(DispatchNotificationCommand([data.captain_user_id], notifications.TOURNAMENT_INVITE_ACCEPTED , [player_name, data.tournament_name], f'/registry/players/profile?id={player_id}', notifications.SUCCESS))
    return JSONResponse({})

@bind_request_body(DeclineInviteRequestData)
@require_logged_in
async def decline_invite(request: Request, body: DeclineInviteRequestData) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    player_id = request.state.user.player_id
    player_name = await handle(GetPlayerNameCommand(player_id))
    data = await handle(GetNotificationSquadDataCommand(tournament_id, body.squad_id))
    command = UnregisterPlayerCommand(tournament_id, body.squad_id, player_id, False)
    await handle(command)
    await handle(DispatchNotificationCommand([data.captain_user_id], notifications.DECLINE_INVITE , [player_name, data.squad_name or data.tournament_name], f'/registry/players/profile?id={player_id}', notifications.WARNING))
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
    user_id = await handle(GetUserIdFromPlayerIdCommand(body.player_id))
    data = await handle(GetNotificationSquadDataCommand(tournament_id, body.squad_id))
    await handle(DispatchNotificationCommand([user_id], notifications.TOURNAMENT_KICKED , [data.squad_name or data.tournament_name], f'/tournaments/details?id={tournament_id}', notifications.WARNING))
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

    user_id = await handle(GetUserIdFromPlayerIdCommand(body.player_id))
    player_name = await handle(GetPlayerNameCommand(body.player_id))
    if body.squad_id:
        data = await handle(GetNotificationSquadDataCommand(tournament_id, body.squad_id))
        await handle(DispatchNotificationCommand([data.captain_user_id], notifications.TOURNAMENT_STAFF_UNREGISTERED_CAPTAIN_NOTIF , [player_name, data.tournament_name], f'/tournaments/details?id={tournament_id}', notifications.WARNING))
        await handle(DispatchNotificationCommand([user_id], notifications.TOURNAMENT_STAFF_UNREGISTERED , [data.tournament_name], f'/tournaments/details?id={tournament_id}', notifications.WARNING))
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

    user_id = await handle(GetUserIdFromPlayerIdCommand(body.player_id))
    data = await handle(GetNotificationSquadDataCommand(tournament_id, body.squad_id))
    await handle(DispatchNotificationCommand([user_id], notifications.CHANGE_SQUAD_CAPTAIN, [data.squad_name or data.tournament_name], f'/tournaments/details?id={tournament_id}', notifications.SUCCESS))
    return JSONResponse({})

@bind_request_body(MakeCaptainRequestData)
@require_tournament_permission(tournament_permissions.REGISTER_TOURNAMENT, check_denied_only=True)
async def add_team_representative(request: Request, body: MakeCaptainRequestData) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    captain_player_id = request.state.user.player_id
    command = CheckSquadCaptainPermissionsCommand(tournament_id, body.squad_id, captain_player_id)
    await handle(command)
    command = AddRepresentativeCommand(tournament_id, body.squad_id, body.player_id)
    await handle(command)
    
    user_id = await handle(GetUserIdFromPlayerIdCommand(body.player_id))
    data = await handle(GetNotificationSquadDataCommand(tournament_id, body.squad_id))
    await handle(DispatchNotificationCommand([user_id], notifications.ADD_REPRESENTATIVE, [data.squad_name or data.tournament_name], f'/tournaments/details?id={tournament_id}', notifications.SUCCESS))
    return JSONResponse({})

@bind_request_body(MakeCaptainRequestData)
@require_tournament_permission(tournament_permissions.REGISTER_TOURNAMENT, check_denied_only=True)
async def remove_team_representative(request: Request, body: MakeCaptainRequestData) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    captain_player_id = request.state.user.player_id
    command = CheckSquadCaptainPermissionsCommand(tournament_id, body.squad_id, captain_player_id)
    await handle(command)
    command = RemoveRepresentativeCommand(tournament_id, body.squad_id, body.player_id)
    await handle(command)

    user_id = await handle(GetUserIdFromPlayerIdCommand(body.player_id))
    data = await handle(GetNotificationSquadDataCommand(tournament_id, body.squad_id))
    await handle(DispatchNotificationCommand([user_id], notifications.REMOVE_REPRESENTATIVE, [data.squad_name or data.tournament_name], f'/tournaments/details?id={tournament_id}', notifications.WARNING))
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

@bind_request_body(UnregisterSquadRequestData)
@require_tournament_permission(tournament_permissions.MANAGE_TOURNAMENT_REGISTRATIONS)
async def force_unregister_squad(request: Request, body: UnregisterSquadRequestData) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    data = await handle(GetNotificationSquadDataCommand(tournament_id, body.squad_id))
    command = UnregisterSquadCommand(tournament_id, body.squad_id)
    await handle(command)

    await handle(DispatchNotificationCommand([data.captain_user_id], notifications.STAFF_UNREGISTER_TEAM, [data.tournament_name], f'/tournaments/details?id={tournament_id}', notifications.WARNING))
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
        print(body.is_approved)
        command = GetSquadRegistrationsCommand(tournament_id, body.registered_only, body.eligible_only, body.hosts_only, body.is_approved)
    else:
        command = GetFFARegistrationsCommand(tournament_id, body.eligible_only, body.hosts_only, body.is_approved)
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

@bind_request_body(TournamentCheckinRequestData)
@require_tournament_permission(tournament_permissions.REGISTER_TOURNAMENT, check_denied_only=True)
async def toggle_checkin(request: Request, body: TournamentCheckinRequestData) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    player_id = request.state.user.player_id
    command = TogglePlayerCheckinCommand(tournament_id, body.squad_id, player_id)
    await handle(command)
    return JSONResponse({})

routes = [
    Route('/api/tournaments/{tournament_id:int}/register', register_me, methods=['POST']),
    Route('/api/tournaments/{tournament_id:int}/forceRegister', force_register_player, methods=['POST']), # dispatches notification
    Route('/api/tournaments/{tournament_id:int}/editRegistration', edit_registration, methods=['POST']), # dispatches notification
    Route('/api/tournaments/{tournament_id:int}/editMyRegistration', edit_my_registration, methods=['POST']),
    Route('/api/tournaments/{tournament_id:int}/createSquad', create_my_squad, methods=['POST']),
    Route('/api/tournaments/{tournament_id:int}/registerTeam', register_my_team, methods=['POST']),
    Route('/api/tournaments/{tournament_id:int}/forceRegisterTeam', force_register_team, methods=['POST']), # dispatches notification
    Route('/api/tournaments/{tournament_id:int}/forceCreateSquad', force_create_squad, methods=['POST']), # dispatches notification
    Route('/api/tournaments/{tournament_id:int}/editSquad', edit_squad, methods=['POST']),
    Route('/api/tournaments/{tournament_id:int}/editMySquad', edit_my_squad, methods=['POST']),
    Route('/api/tournaments/{tournament_id:int}/invitePlayer', invite_player, methods=['POST']), # dispatches notification
    Route('/api/tournaments/{tournament_id:int}/acceptInvite', accept_invite, methods=['POST']), # dispatches notification
    Route('/api/tournaments/{tournament_id:int}/declineInvite', decline_invite, methods=['POST']), # dispatches notification
    Route('/api/tournaments/{tournament_id:int}/kickPlayer', remove_player_from_squad, methods=['POST']), # dispatches notification
    Route('/api/tournaments/{tournament_id:int}/unregister', unregister_me, methods=['POST']),
    Route('/api/tournaments/{tournament_id:int}/forceUnregister', staff_unregister, methods=['POST']), # dispatches notification
    Route('/api/tournaments/{tournament_id:int}/makeCaptain', change_squad_captain, methods=['POST']), # dispatches notification
    Route('/api/tournaments/{tournament_id:int}/addRepresentative', add_team_representative, methods=['POST']), # dispatches notification
    Route('/api/tournaments/{tournament_id:int}/removeRepresentative', remove_team_representative, methods=['POST']), # dispatches notification
    Route('/api/tournaments/{tournament_id:int}/unregisterSquad', unregister_squad, methods=['POST']),
    Route('/api/tournaments/{tournament_id:int}/forceUnregisterSquad', force_unregister_squad, methods=['POST']), # dispatches notification
    Route('/api/tournaments/{tournament_id:int}/squads/{squad_id:int}', view_squad),
    Route('/api/tournaments/{tournament_id:int}/registrations', list_registrations),
    Route('/api/tournaments/{tournament_id:int}/myRegistration', my_registration),
    Route('/api/tournaments/{tournament_id:int}/toggleCheckin', toggle_checkin, methods=['POST'])
]