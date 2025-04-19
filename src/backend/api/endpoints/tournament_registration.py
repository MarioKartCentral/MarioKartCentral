from starlette.requests import Request
from starlette.routing import Route
from starlette.background import BackgroundTask
from api.auth import require_logged_in, require_tournament_permission, check_tournament_visiblity
from api.data import handle
from api.utils.responses import JSONResponse, bind_request_body, bind_request_query
from common.auth import tournament_permissions
from common.data.commands import *
from common.data.models import *
from api.utils.word_filter import check_word_filter
import common.data.notifications as notifications

# endpoint used when a user creates their own squad
@bind_request_body(CreateSquadRequestData)
@check_word_filter
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
@check_word_filter
@require_tournament_permission(tournament_permissions.REGISTER_TOURNAMENT, check_denied_only=True)
async def register_my_team(request: Request, body: RegisterTeamRequestData) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    player_id = request.state.user.player_id
    command = RegisterTeamTournamentCommand(tournament_id, body.squad_name, body.squad_tag, body.squad_color,
                                            player_id, body.roster_ids, body.players, False)
    await handle(command)
    return JSONResponse({})

@bind_request_body(RegisterTeamRequestData)
@check_word_filter
@require_tournament_permission(tournament_permissions.MANAGE_TOURNAMENT_REGISTRATIONS)
async def force_register_team(request: Request, body: RegisterTeamRequestData) -> JSONResponse:
    async def notify():
        if registration_id:
            data = await handle(GetNotificationSquadDataCommand(tournament_id, registration_id))
            await handle(DispatchNotificationCommand([data.captain_user_id], notifications.STAFF_REGISTER_TEAM, {'tournament_name': data.tournament_name}, f'/tournaments/details?id={tournament_id}', notifications.SUCCESS))

    tournament_id = request.path_params['tournament_id']
    player_id = request.state.user.player_id
    command = RegisterTeamTournamentCommand(tournament_id, body.squad_name, body.squad_tag, body.squad_color,
                                            player_id, body.roster_ids, body.players, True, is_privileged=True)
    registration_id = await handle(command)
    return JSONResponse({}, background=BackgroundTask(notify))

# endpoint used when a tournament staff creates a squad with another user in it
@bind_request_body(ForceCreateSquadRequestData)
@check_word_filter
@require_tournament_permission(tournament_permissions.MANAGE_TOURNAMENT_REGISTRATIONS)
async def force_create_squad(request: Request, body: ForceCreateSquadRequestData) -> JSONResponse:
    async def notify():
        tournament_name = await handle(GetTournamentNameFromIdCommand(tournament_id))
        user_id = await handle(GetUserIdFromPlayerIdCommand(body.player_id))
        if user_id is None:
            return
        await handle(DispatchNotificationCommand([user_id], notifications.STAFF_CREATE_SQUAD, {'tournament_name': tournament_name}, f'/tournaments/details?id={tournament_id}', notifications.INFO))

    tournament_id = request.path_params['tournament_id']
    command = CreateSquadCommand(body.squad_name, body.squad_tag, body.squad_color, body.player_id, tournament_id, 
        body.is_checked_in, body.is_bagger_clause, body.mii_name, body.can_host, body.selected_fc_id, body.is_approved, is_privileged=True)
    await handle(command)
    return JSONResponse({}, background=BackgroundTask(notify))

@bind_request_body(EditSquadRequestData)
@check_word_filter
@require_tournament_permission(tournament_permissions.MANAGE_TOURNAMENT_REGISTRATIONS)
async def edit_squad(request: Request, body: EditSquadRequestData) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    command = EditSquadCommand(tournament_id, body.registration_id, body.squad_name, body.squad_tag, body.squad_color, body.is_registered, body.is_approved)
    await handle(command)
    return JSONResponse({})

@bind_request_body(EditMySquadRequestData)
@check_word_filter
@require_tournament_permission(tournament_permissions.REGISTER_TOURNAMENT, check_denied_only=True)
async def edit_my_squad(request: Request, body: EditMySquadRequestData) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    captain_player_id = request.state.user.player_id
    command = CheckSquadCaptainPermissionsCommand(tournament_id, body.registration_id, captain_player_id)
    await handle(command)
    command = EditSquadCommand(tournament_id, body.registration_id, body.squad_name, body.squad_tag, body.squad_color, True, None)
    await handle(command)
    return JSONResponse({})

# used when the captain of a squad invites a player to their squad.
# use force_register_player in tournament staff contexts
@bind_request_body(InvitePlayerRequestData)
@require_tournament_permission(tournament_permissions.REGISTER_TOURNAMENT, check_denied_only=True)
async def invite_player(request: Request, body: InvitePlayerRequestData) -> JSONResponse:
    async def notify():
        user_id = await handle(GetUserIdFromPlayerIdCommand(body.player_id))
        if user_id is None:
            return
        data = await handle(GetNotificationSquadDataCommand(tournament_id, body.registration_id))
        content_args = {'squad_name': data.squad_name or '', 'tournament_name': data.tournament_name}
        await handle(DispatchNotificationCommand([user_id], notifications.TOURNAMENT_INVITE , content_args, '/registry/invites', notifications.SUCCESS))

    tournament_id = request.path_params['tournament_id']
    captain_player_id = request.state.user.player_id
    command = CheckSquadCaptainPermissionsCommand(tournament_id, body.registration_id, captain_player_id)
    await handle(command)
    command = RegisterPlayerCommand(body.player_id, tournament_id, body.registration_id, False, False, None, False, True, None, body.is_representative, body.is_bagger_clause, False, False)
    await handle(command)
    return JSONResponse({}, background=BackgroundTask(notify))

# endpoint used when a user registers themself for a tournament
@bind_request_body(RegisterPlayerRequestData)
@check_word_filter
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
@check_word_filter
@require_tournament_permission(tournament_permissions.MANAGE_TOURNAMENT_REGISTRATIONS)
async def force_register_player(request: Request, body: ForceRegisterPlayerRequestData) -> JSONResponse:
    async def notify():
        user_id = await handle(GetUserIdFromPlayerIdCommand(body.player_id))
        if user_id is None:
            return
        player_name = await handle(GetPlayerNameCommand(body.player_id))
        if body.registration_id:
            data = await handle(GetNotificationSquadDataCommand(tournament_id, body.registration_id))
            content_args = {'player_name': player_name, 'tournament_name': data.tournament_name}
            await handle(DispatchNotificationCommand([data.captain_user_id], notifications.TOURNAMENT_STAFF_REGISTERED_CAPTAIN_NOTIF , content_args, f'/tournaments/details?id={tournament_id}', notifications.INFO))
            await handle(DispatchNotificationCommand([user_id], notifications.TOURNAMENT_STAFF_REGISTERED , {'tournament_name': data.tournament_name}, f'/tournaments/details?id={tournament_id}', notifications.SUCCESS))

    tournament_id = request.path_params['tournament_id']
    command = RegisterPlayerCommand(body.player_id, tournament_id, body.registration_id, body.is_squad_captain, body.is_checked_in, 
        body.mii_name, body.can_host, body.is_invite, body.selected_fc_id, body.is_representative, body.is_bagger_clause, body.is_approved, True)
    await handle(command)
    return JSONResponse({}, background=BackgroundTask(notify))

@bind_request_body(EditPlayerRegistrationRequestData)
@check_word_filter
@require_tournament_permission(tournament_permissions.MANAGE_TOURNAMENT_REGISTRATIONS)
async def edit_registration(request: Request, body: EditPlayerRegistrationRequestData) -> JSONResponse:
    async def notify():
        tournament_name = await handle(GetTournamentNameFromIdCommand(tournament_id))
        user_id = await handle(GetUserIdFromPlayerIdCommand(body.player_id))
        if user_id is None:
            return
        await handle(DispatchNotificationCommand([user_id], notifications.STAFF_EDIT_PLAYER_REGISTRATION , {'tournament_name': tournament_name}, f'/tournaments/details?id={tournament_id}', notifications.INFO))

    tournament_id = request.path_params['tournament_id']
    command = EditPlayerRegistrationCommand(tournament_id, body.registration_id, body.player_id, body.mii_name, body.can_host,
        body.is_invite, body.is_checked_in, body.is_squad_captain, body.selected_fc_id, body.is_representative, 
        body.is_bagger_clause, body.is_approved, True)
    await handle(command)
    return JSONResponse({}, background=BackgroundTask(notify))

@bind_request_body(EditMyRegistrationRequestData)
@check_word_filter
@require_tournament_permission(tournament_permissions.REGISTER_TOURNAMENT, check_denied_only=True)
async def edit_my_registration(request: Request, body: EditMyRegistrationRequestData) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    player_id = request.state.user.player_id
    player_host_permission = await handle(CheckUserHasPermissionCommand(request.state.user.id, tournament_permissions.REGISTER_HOST, True, 
                                                                        tournament_id=tournament_id))
    if body.can_host and not player_host_permission:
        raise Problem("User does not have permission to register as a host", status=401)
    command = EditPlayerRegistrationCommand(tournament_id, body.registration_id, player_id, body.mii_name, body.can_host, False, None, None, body.selected_fc_id,
                                            None, None, None, False)
    await handle(command)
    return JSONResponse({})

@bind_request_body(AcceptInviteRequestData)
@check_word_filter
@require_tournament_permission(tournament_permissions.REGISTER_TOURNAMENT, check_denied_only=True)
async def accept_invite(request: Request, body: AcceptInviteRequestData) -> JSONResponse:
    async def notify():
        player_name = await handle(GetPlayerNameCommand(player_id))
        data = await handle(GetNotificationSquadDataCommand(tournament_id, body.registration_id))
        content_args = {'player_name': player_name, 'tournament_name': data.tournament_name}
        await handle(DispatchNotificationCommand([data.captain_user_id], notifications.TOURNAMENT_INVITE_ACCEPTED , content_args, f'/tournaments/details?id={tournament_id}', notifications.SUCCESS))

    tournament_id = request.path_params['tournament_id']
    player_id = request.state.user.player_id
    player_host_permission = await handle(CheckUserHasPermissionCommand(request.state.user.id, tournament_permissions.REGISTER_HOST, True, 
                                                                        tournament_id=tournament_id))
    if body.can_host and not player_host_permission:
        raise Problem("User does not have permission to register as a host", status=401)
    
    command = EditPlayerRegistrationCommand(tournament_id, body.registration_id, player_id, body.mii_name, body.can_host,
        False, False, False, body.selected_fc_id, None, None, None, False)
    await handle(command)
    return JSONResponse({}, background=BackgroundTask(notify))

@bind_request_body(DeclineInviteRequestData)
@require_logged_in
async def decline_invite(request: Request, body: DeclineInviteRequestData) -> JSONResponse:
    async def notify():
        data = await handle(GetNotificationSquadDataCommand(tournament_id, body.registration_id))
        player_name = await handle(GetPlayerNameCommand(player_id))
        content_args = {'player_name': player_name, 'squad_name': data.squad_name or data.tournament_name}
        await handle(DispatchNotificationCommand([data.captain_user_id], notifications.DECLINE_SQUAD_INVITE , content_args, f'/tournaments/details?id={tournament_id}', notifications.WARNING))

    tournament_id = request.path_params['tournament_id']
    player_id = request.state.user.player_id
    command = UnregisterPlayerCommand(tournament_id, body.registration_id, player_id, False)
    await handle(command)
    return JSONResponse({}, background=BackgroundTask(notify))

# used when a squad captain wants to remove a member from their squad
@bind_request_body(KickSquadPlayerRequestData)
@require_tournament_permission(tournament_permissions.REGISTER_TOURNAMENT, check_denied_only=True)
async def remove_player_from_squad(request: Request, body: KickSquadPlayerRequestData) -> JSONResponse:
    async def notify():
        user_id = await handle(GetUserIdFromPlayerIdCommand(body.player_id))
        if user_id is None:
            return
        data = await handle(GetNotificationSquadDataCommand(tournament_id, body.registration_id))
        content_args = {'squad_name': data.squad_name or data.tournament_name}
        await handle(DispatchNotificationCommand([user_id], notifications.TOURNAMENT_KICKED , content_args, f'/tournaments/details?id={tournament_id}', notifications.WARNING))

    tournament_id = request.path_params['tournament_id']
    captain_player_id = request.state.user.player_id
    command = CheckSquadCaptainPermissionsCommand(tournament_id, body.registration_id, captain_player_id)
    await handle(command)
    command = UnregisterPlayerCommand(tournament_id, body.registration_id, body.player_id, False)
    await handle(command)
    return JSONResponse({}, background=BackgroundTask(notify))

# used when a player unregisters themself from the tournament
@bind_request_body(UnregisterPlayerRequestData)
@require_logged_in
async def unregister_me(request: Request, body: UnregisterPlayerRequestData) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    player_id = request.state.user.player_id
    command = UnregisterPlayerCommand(tournament_id, body.registration_id, player_id, False)
    await handle(command)
    return JSONResponse({})

# used when a staff member force removes a player from the tournament
@bind_request_body(StaffUnregisterPlayerRequestData)
@require_tournament_permission(tournament_permissions.MANAGE_TOURNAMENT_REGISTRATIONS)
async def staff_unregister(request: Request, body: StaffUnregisterPlayerRequestData) -> JSONResponse:
    async def notify():
        user_id = await handle(GetUserIdFromPlayerIdCommand(body.player_id))
        if user_id is None:
            return
        player_name = await handle(GetPlayerNameCommand(body.player_id))
        if body.registration_id:
            data = await handle(GetNotificationSquadDataCommand(tournament_id, body.registration_id))
            content_args = {'player_name': player_name, 'tournament_name': data.tournament_name}
            await handle(DispatchNotificationCommand([data.captain_user_id], notifications.TOURNAMENT_STAFF_UNREGISTERED_CAPTAIN_NOTIF , content_args, f'/tournaments/details?id={tournament_id}', notifications.WARNING))
            await handle(DispatchNotificationCommand([user_id], notifications.TOURNAMENT_STAFF_UNREGISTERED , {'tournament_name': data.tournament_name}, f'/tournaments/details?id={tournament_id}', notifications.WARNING))

    tournament_id = request.path_params['tournament_id']
    command = UnregisterPlayerCommand(tournament_id, body.registration_id, body.player_id, True)
    await handle(command)
    return JSONResponse({}, background=BackgroundTask(notify))

@bind_request_body(MakeCaptainRequestData)
@require_tournament_permission(tournament_permissions.REGISTER_TOURNAMENT, check_denied_only=True)
async def change_squad_captain(request: Request, body: MakeCaptainRequestData) -> JSONResponse:
    async def notify():
        user_id = await handle(GetUserIdFromPlayerIdCommand(body.player_id))
        if user_id is None:
            return
        data = await handle(GetNotificationSquadDataCommand(tournament_id, body.registration_id))
        content_args = {'squad_name': data.squad_name or data.tournament_name}
        await handle(DispatchNotificationCommand([user_id], notifications.CHANGE_SQUAD_CAPTAIN, content_args, f'/tournaments/details?id={tournament_id}', notifications.SUCCESS))

    tournament_id = request.path_params['tournament_id']
    captain_player_id = request.state.user.player_id
    command = CheckSquadCaptainPermissionsCommand(tournament_id, body.registration_id, captain_player_id)
    await handle(command)
    command = ChangeSquadCaptainCommand(tournament_id, body.registration_id, body.player_id)
    await handle(command)
    return JSONResponse({}, background=BackgroundTask(notify))

@bind_request_body(MakeCaptainRequestData)
@require_tournament_permission(tournament_permissions.REGISTER_TOURNAMENT, check_denied_only=True)
async def add_team_representative(request: Request, body: MakeCaptainRequestData) -> JSONResponse:
    async def notify():
        user_id = await handle(GetUserIdFromPlayerIdCommand(body.player_id))
        if user_id is None:
            return
        data = await handle(GetNotificationSquadDataCommand(tournament_id, body.registration_id))
        content_args = {'squad_name': data.squad_name or data.tournament_name}
        await handle(DispatchNotificationCommand([user_id], notifications.ADD_REPRESENTATIVE, content_args, f'/tournaments/details?id={tournament_id}', notifications.SUCCESS))

    tournament_id = request.path_params['tournament_id']
    captain_player_id = request.state.user.player_id
    command = CheckSquadCaptainPermissionsCommand(tournament_id, body.registration_id, captain_player_id)
    await handle(command)
    command = AddRepresentativeCommand(tournament_id, body.registration_id, body.player_id)
    await handle(command)
    return JSONResponse({}, background=BackgroundTask(notify))

@bind_request_body(MakeCaptainRequestData)
@require_tournament_permission(tournament_permissions.REGISTER_TOURNAMENT, check_denied_only=True)
async def remove_team_representative(request: Request, body: MakeCaptainRequestData) -> JSONResponse:
    async def notify():
        user_id = await handle(GetUserIdFromPlayerIdCommand(body.player_id))
        if user_id is None:
            return
        data = await handle(GetNotificationSquadDataCommand(tournament_id, body.registration_id))
        content_args = {'squad_name': data.squad_name or data.tournament_name}
        await handle(DispatchNotificationCommand([user_id], notifications.REMOVE_REPRESENTATIVE, content_args, f'/tournaments/details?id={tournament_id}', notifications.WARNING))

    tournament_id = request.path_params['tournament_id']
    captain_player_id = request.state.user.player_id
    command = CheckSquadCaptainPermissionsCommand(tournament_id, body.registration_id, captain_player_id)
    await handle(command)
    command = RemoveRepresentativeCommand(tournament_id, body.registration_id, body.player_id)
    await handle(command)
    return JSONResponse({}, background=BackgroundTask(notify))

@bind_request_body(UnregisterSquadRequestData)
@require_logged_in
async def unregister_squad(request: Request, body: UnregisterSquadRequestData) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    captain_player_id = request.state.user.player_id
    command = CheckSquadCaptainPermissionsCommand(tournament_id, body.registration_id, captain_player_id)
    await handle(command)
    command = UnregisterSquadCommand(tournament_id, body.registration_id)
    await handle(command)
    return JSONResponse({})

@bind_request_body(UnregisterSquadRequestData)
@require_tournament_permission(tournament_permissions.MANAGE_TOURNAMENT_REGISTRATIONS)
async def force_unregister_squad(request: Request, body: UnregisterSquadRequestData) -> JSONResponse:
    async def notify():
        await handle(DispatchNotificationCommand([data.captain_user_id], notifications.STAFF_UNREGISTER_TEAM, {'tournament_name': data.tournament_name}, f'/tournaments/details?id={tournament_id}', notifications.WARNING))

    tournament_id = request.path_params['tournament_id']

    try: # get data before main command
        data = await handle(GetNotificationSquadDataCommand(tournament_id, body.registration_id))
    except Exception:
        pass
    
    command = UnregisterSquadCommand(tournament_id, body.registration_id)
    await handle(command)
    return JSONResponse({}, background=BackgroundTask(notify))

async def view_squad(request: Request) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    registration_id = request.path_params['registration_id']
    command = GetSquadDetailsCommand(tournament_id, registration_id)
    squad = await handle(command)
    return JSONResponse(squad)

@bind_request_query(TournamentRegistrationFilter)
@check_tournament_visiblity
async def list_registrations(request: Request, body: TournamentRegistrationFilter) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    command = GetTournamentRegistrationsCommand(tournament_id, body.registered_only, body.eligible_only, body.hosts_only, body.is_approved)
    registrations = await handle(command)
    return JSONResponse(registrations)

@require_logged_in
async def my_registration(request: Request) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    player_id = request.state.user.player_id
    if not player_id:
        return JSONResponse(None)
    command = GetPlayerRegistrationCommand(tournament_id, request.state.user.player_id)
    registrations = await handle(command)
    return JSONResponse(registrations)

@bind_request_body(TournamentCheckinRequestData)
@require_tournament_permission(tournament_permissions.REGISTER_TOURNAMENT, check_denied_only=True)
async def toggle_checkin(request: Request, body: TournamentCheckinRequestData) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    player_id = request.state.user.player_id
    command = TogglePlayerCheckinCommand(tournament_id, body.registration_id, player_id)
    await handle(command)
    return JSONResponse({})

@bind_request_body(AddRemoveRosterRequestData)
@require_tournament_permission(tournament_permissions.REGISTER_TOURNAMENT, check_denied_only=True)
async def add_roster_to_squad(request: Request, body: AddRemoveRosterRequestData) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    player_id = request.state.user.player_id
    command = AddRosterToSquadCommand(tournament_id, body.registration_id, body.roster_id, player_id)
    await handle(command)
    return JSONResponse({})

@bind_request_body(AddRemoveRosterRequestData)
@require_tournament_permission(tournament_permissions.REGISTER_TOURNAMENT, check_denied_only=True)
async def remove_roster_from_squad(request: Request, body: AddRemoveRosterRequestData) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    player_id = request.state.user.player_id
    command = RemoveRosterFromSquadCommand(tournament_id, body.registration_id, body.roster_id, player_id)
    await handle(command)
    return JSONResponse({})

@bind_request_body(AddRemoveRosterRequestData)
@require_tournament_permission(tournament_permissions.MANAGE_TOURNAMENT_REGISTRATIONS)
async def force_add_roster_to_squad(request: Request, body: AddRemoveRosterRequestData) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    command = AddRosterToSquadCommand(tournament_id, body.registration_id, body.roster_id, None, True)
    await handle(command)
    return JSONResponse({})

@bind_request_body(AddRemoveRosterRequestData)
@require_tournament_permission(tournament_permissions.MANAGE_TOURNAMENT_REGISTRATIONS)
async def force_remove_roster_from_squad(request: Request, body: AddRemoveRosterRequestData) -> JSONResponse:
    tournament_id = request.path_params['tournament_id']
    command = RemoveRosterFromSquadCommand(tournament_id, body.registration_id, body.roster_id, None, True)
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
    Route('/api/tournaments/{tournament_id:int}/squads/{registration_id:int}', view_squad),
    Route('/api/tournaments/{tournament_id:int}/registrations', list_registrations),
    Route('/api/tournaments/{tournament_id:int}/myRegistration', my_registration),
    Route('/api/tournaments/{tournament_id:int}/toggleCheckin', toggle_checkin, methods=['POST']),
    Route('/api/tournaments/{tournament_id:int}/addRosterToSquad', add_roster_to_squad, methods=['POST']),
    Route('/api/tournaments/{tournament_id:int}/removeRosterFromSquad', remove_roster_from_squad, methods=['POST']),
    Route('/api/tournaments/{tournament_id:int}/forceAddRosterToSquad', force_add_roster_to_squad, methods=['POST']),
    Route('/api/tournaments/{tournament_id:int}/forceRemoveRosterFromSquad', force_remove_roster_from_squad, methods=['POST']),
]