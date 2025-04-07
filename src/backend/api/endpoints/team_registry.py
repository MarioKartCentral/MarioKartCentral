from starlette.requests import Request
from starlette.routing import Route
from starlette.background import BackgroundTask
from api.auth import require_permission, require_logged_in, require_team_permission
from api.data import handle
from datetime import datetime
from api.utils.responses import JSONResponse, bind_request_body, bind_request_query
from common.auth import permissions
from common.auth import team_permissions
from common.data.commands import *
from common.data.models import *
from api.utils.word_filter import check_word_filter
import common.data.notifications as notifications

# for moderator use, does not go to approval queue
@bind_request_body(CreateTeamRequestData)
@check_word_filter
@require_permission(permissions.MANAGE_TEAMS)
async def create_team(request: Request, body: CreateTeamRequestData) -> JSONResponse:
    command = CreateTeamCommand(body.name, body.tag, body.description, body.language, body.color,
        body.logo_file, body.approval_status, body.is_historical, body.game, body.mode, body.is_recruiting, body.is_active, True)
    team_id = await handle(command)
    return JSONResponse({'id': team_id})

@bind_request_body(RequestCreateTeamRequestData)
@check_word_filter
@require_permission(permissions.CREATE_TEAM, check_denied_only=True)
async def request_create_team(request: Request, body: RequestCreateTeamRequestData) -> JSONResponse:
    approval_status = "pending"
    command = CreateTeamCommand(body.name, body.tag, body.description, body.language, body.color,
                                body.logo_file, approval_status, False, body.game, body.mode, body.is_recruiting, 
                                True, False, user_id=request.state.user.id)
    team_id = await handle(command)
    return JSONResponse({'id': team_id})

async def view_team(request: Request) -> JSONResponse:
    team_id = request.path_params['team_id']
    command = GetTeamInfoCommand(team_id)
    team = await handle(command)
    return JSONResponse(team)

# for moderator use, allows for direct editing of name/tags and approving/disapproving teams
@bind_request_body(EditTeamRequestData)
@check_word_filter
@require_permission(permissions.MANAGE_TEAMS)
async def edit_team(request: Request, body: EditTeamRequestData) -> JSONResponse:
    async def notify():
        user_ids = await handle(GetTeamManagerAndLeaderUserIdsCommand(body.team_id))
        await handle(DispatchNotificationCommand(user_ids, notifications.STAFF_TEAM_EDIT, {'team_name': team_name}, f'/registry/teams/profile?id={body.team_id}', notifications.WARNING))

    try: # get data before edit
        team_name = await handle(GetTeamNameFromIdCommand(body.team_id))
    except Exception:
        pass

    mod_player_id = request.state.user.player_id
    command = EditTeamCommand(body.team_id, body.name, body.tag, body.description, body.language, body.color,
        body.logo_file, body.remove_logo, body.approval_status, body.is_historical, True, mod_player_id)
    await handle(command)

    return JSONResponse({}, background=BackgroundTask(notify))

@require_permission(permissions.MANAGE_TEAMS)
async def approve_team(request: Request) -> JSONResponse:
    async def notify():
        user_ids = await handle(GetTeamManagerAndLeaderUserIdsCommand(team_id))
        team_name = await handle(GetTeamNameFromIdCommand(team_id))
        await handle(DispatchNotificationCommand(user_ids, notifications.TEAM_APPROVED , {'team_name': team_name}, f'/registry/teams/profile?id={team_id}', notifications.SUCCESS))

    team_id = request.path_params['team_id']
    command = ApproveDenyTeamCommand(team_id, 'approved')
    await handle(command)
    return JSONResponse({}, background=BackgroundTask(notify))

@require_permission(permissions.MANAGE_TEAMS)
async def deny_team(request: Request) -> JSONResponse:
    async def notify():
        user_ids = await handle(GetTeamManagerAndLeaderUserIdsCommand(team_id))
        team_name = await handle(GetTeamNameFromIdCommand(team_id))
        await handle(DispatchNotificationCommand(user_ids, notifications.TEAM_DENIED , {'team_name': team_name}, f'/registry/teams/profile?id={team_id}', notifications.WARNING))

    team_id = request.path_params['team_id']
    command = ApproveDenyTeamCommand(team_id, 'denied')
    await handle(command)
    return JSONResponse({}, background=BackgroundTask(notify))

# for editing non-essential team info such as description, color, etc
@bind_request_body(ManagerEditTeamRequestData)
@check_word_filter
@require_team_permission(team_permissions.EDIT_TEAM_INFO)
async def manager_edit_team(request: Request, body: ManagerEditTeamRequestData) -> JSONResponse:
    command = ManagerEditTeamCommand(body.team_id, body.description, body.language, body.color, body.logo_file, body.remove_logo)
    await handle(command)
    return JSONResponse({})

# for editing team name/tag, which requires moderator approval
@bind_request_body(RequestEditTeamRequestData)
@check_word_filter
@require_team_permission(team_permissions.EDIT_TEAM_INFO)
async def request_edit_team(request: Request, body: RequestEditTeamRequestData) -> JSONResponse:
    command = RequestEditTeamCommand(body.team_id, body.name, body.tag)
    await handle(command)
    return JSONResponse({})

@bind_request_body(ApproveTeamEditRequestData)
@require_permission(permissions.MANAGE_TEAMS)
async def approve_team_edit_request(request: Request, body: ApproveTeamEditRequestData) -> JSONResponse:
    async def notify():
        data = await handle(GetNotificationTeamDataFromEditRequestCommand(body.request_id))
        user_ids = await handle(GetTeamManagerAndLeaderUserIdsCommand(data.team_id))
        await handle(DispatchNotificationCommand(user_ids, notifications.TEAM_CHANGE_ACCEPTED, {'team_name': data.team_name}, f'/registry/teams/profile?id={data.team_id}', notifications.SUCCESS))

    mod_player_id = request.state.user.player_id
    command = ApproveTeamEditCommand(body.request_id, mod_player_id)
    await handle(command)
    return JSONResponse({}, background=BackgroundTask(notify))

@bind_request_body(DenyTeamEditRequestData)
@require_permission(permissions.MANAGE_TEAMS)
async def deny_team_edit_request(request: Request, body: DenyTeamEditRequestData) -> JSONResponse:
    async def notify():
        data = await handle(GetNotificationTeamDataFromEditRequestCommand(body.request_id))
        user_ids = await handle(GetTeamManagerAndLeaderUserIdsCommand(data.team_id))
        await handle(DispatchNotificationCommand(user_ids, notifications.TEAM_CHANGE_DENIED, {'team_name': data.team_name}, f'/registry/teams/profile?id={data.team_id}', notifications.WARNING))

    mod_player_id = request.state.user.player_id
    command = DenyTeamEditCommand(body.request_id, mod_player_id)
    await handle(command)
    return JSONResponse({}, background=BackgroundTask(notify))

@bind_request_query(TeamEditFilter)
@require_permission(permissions.MANAGE_TEAMS)
async def list_team_edit_requests(request: Request, filter: TeamEditFilter) -> JSONResponse:
    command = ListTeamEditRequestsCommand(filter)
    requests = await handle(command)
    return JSONResponse(requests)

# for moderator use, does not go to approval queue
@bind_request_body(CreateRosterRequestData)
@check_word_filter
@require_permission(permissions.MANAGE_TEAMS)
async def create_roster(request: Request, body: CreateRosterRequestData) -> JSONResponse:
    command = CreateRosterCommand(body.team_id, body.game, body.mode, body.name, body.tag, body.is_recruiting, body.is_active, body.approval_status)
    await handle(command)
    return JSONResponse({})

@bind_request_body(RequestCreateRosterRequestData)
@check_word_filter
@require_team_permission(team_permissions.CREATE_ROSTERS)
async def request_create_roster(request: Request, body: RequestCreateRosterRequestData) -> JSONResponse:
    command = CreateRosterCommand(body.team_id, body.game, body.mode, body.name, body.tag, body.is_recruiting, True, "pending")
    await handle(command)
    return JSONResponse({})

# for moderator use, allows for direct editing of name/tags
@bind_request_body(EditRosterRequestData)
@check_word_filter
@require_permission(permissions.MANAGE_TEAMS)
async def edit_roster(request: Request, body: EditRosterRequestData) -> JSONResponse:
    async def notify():
        user_ids = await handle(GetTeamManagerAndLeaderUserIdsCommand(body.team_id))
        content_args = {'roster_name': data.roster_name or data.team_name}
        await handle(DispatchNotificationCommand(user_ids, notifications.STAFF_ROSTER_EDIT, content_args, f'/registry/teams/profile?id={body.team_id}', notifications.WARNING))

    try: # get data before edit
        data = await handle(GetNotificationTeamRosterDataCommand(body.roster_id))
    except Exception:
        pass

    mod_player_id = request.state.user.player_id
    command = EditRosterCommand(body.roster_id, body.team_id, body.name, body.tag, body.is_recruiting,
                                body.is_active, body.approval_status, mod_player_id)
    await handle(command)
    return JSONResponse({}, background=BackgroundTask(notify))

@bind_request_body(ManagerEditRosterRequestData)
@require_team_permission(team_permissions.MANAGE_ROSTERS)
async def manager_edit_roster(request: Request, body: ManagerEditRosterRequestData) -> JSONResponse:
    command = ManagerEditRosterCommand(body.roster_id, body.team_id, body.is_recruiting)
    await handle(command)
    return JSONResponse({})

@bind_request_body(RequestEditRosterRequestData)
@require_team_permission(team_permissions.MANAGE_ROSTERS)
async def request_edit_roster(request: Request, body: RequestEditRosterRequestData) -> JSONResponse:
    command = RequestEditRosterCommand(body.roster_id, body.team_id, body.name, body.tag)
    await handle(command)
    return JSONResponse({})

@bind_request_body(EditRosterChangeRequestData)
@require_permission(permissions.MANAGE_TEAMS)
async def approve_roster_edit_request(request: Request, body: EditRosterChangeRequestData) -> JSONResponse:
    async def notify():
        data = await handle(GetNotificationTeamRosterDataFromRosterEditRequestCommand(body.request_id)) # get data before edit
        user_ids = await handle(GetTeamManagerAndLeaderUserIdsCommand(data.team_id))
        content_args = {'roster_name': data.roster_name or data.team_name}
        await handle(DispatchNotificationCommand(user_ids, notifications.ROSTER_CHANGE_ACCEPTED, content_args, f'/registry/teams/profile?id={data.team_id}', notifications.SUCCESS))

    mod_player_id = request.state.user.player_id
    command = ApproveRosterEditCommand(body.request_id, mod_player_id)
    await handle(command)
    return JSONResponse({}, background=BackgroundTask(notify))

@bind_request_body(EditRosterChangeRequestData)
@require_permission(permissions.MANAGE_TEAMS)
async def deny_roster_edit_request(request: Request, body: EditRosterChangeRequestData) -> JSONResponse:
    async def notify():
        data = await handle(GetNotificationTeamRosterDataFromRosterEditRequestCommand(body.request_id))
        user_ids = await handle(GetTeamManagerAndLeaderUserIdsCommand(data.team_id))
        content_args = {'roster_name': data.roster_name or data.team_name}
        await handle(DispatchNotificationCommand(user_ids, notifications.ROSTER_CHANGE_DENIED, content_args, f'/registry/teams/profile?id={data.team_id}', notifications.WARNING))

    mod_player_id = request.state.user.player_id
    command = DenyRosterEditCommand(body.request_id, mod_player_id)
    await handle(command)
    return JSONResponse({}, background=BackgroundTask(notify))

@bind_request_body(InviteRosterPlayerRequestData)
@require_team_permission(team_permissions.INVITE_PLAYERS)
@require_permission(permissions.INVITE_TO_TEAM, check_denied_only=True)
async def invite_player(request: Request, body: InviteRosterPlayerRequestData) -> JSONResponse:
    async def notify():
        user_id = await handle(GetUserIdFromPlayerIdCommand(body.player_id))
        if user_id is None:
            return
        data = await handle(GetNotificationTeamRosterDataCommand(body.roster_id))
        content_args = {'roster_name': data.roster_name or data.team_name}
        await handle(DispatchNotificationCommand([user_id], notifications.TEAM_INVITE , content_args, '/registry/invites', notifications.SUCCESS))

    command = InvitePlayerCommand(body.player_id, body.roster_id, body.team_id, body.is_bagger_clause)
    await handle(command)
    return JSONResponse({}, background=BackgroundTask(notify))

@bind_request_body(DeleteInviteRequestData)
@require_team_permission(team_permissions.INVITE_PLAYERS)
async def delete_invite(request: Request, body: DeleteInviteRequestData) -> JSONResponse:
    command = DeleteInviteCommand(body.player_id, body.roster_id, body.team_id)
    await handle(command)
    return JSONResponse({})

@bind_request_body(DeleteInviteRequestData)
@require_permission(permissions.MANAGE_TEAMS)
async def mod_delete_invite(request: Request, body: DeleteInviteRequestData) -> JSONResponse:
    command = DeleteInviteCommand(body.player_id, body.roster_id, body.team_id)
    await handle(command)
    return JSONResponse({})

@bind_request_body(AcceptRosterInviteRequestData)
@require_permission(permissions.JOIN_TEAM, check_denied_only=True)
async def accept_invite(request: Request, body: AcceptRosterInviteRequestData) -> JSONResponse:
    async def notify():
        data = await handle(GetNotificationDataFromTeamTransfersCommand(body.invite_id))
        user_ids = await handle(GetTeamManagerAndLeaderUserIdsCommand(data.team_id))
        content_args = {'player_name': data.player_name, 'roster_name': data.roster_name or data.team_name}
        await handle(DispatchNotificationCommand(user_ids, notifications.TEAM_INVITE_ACCEPTED, content_args, f'/registry/players/profile?id={request.state.user.player_id}', notifications.SUCCESS))

    command = AcceptInviteCommand(body.invite_id, body.roster_leave_id, request.state.user.player_id)
    await handle(command)
    return JSONResponse({}, background=BackgroundTask(notify))

@bind_request_body(DeclineRosterInviteRequestData)
@require_logged_in
async def decline_invite(request: Request, body: DeclineRosterInviteRequestData) -> JSONResponse:
    async def notify():
        content_args = {'player_name': data.player_name, 'roster_name': data.roster_name or data.team_name}
        await handle(DispatchNotificationCommand(user_ids, notifications.DECLINE_INVITE, content_args, f'/registry/players/profile?id={request.state.user.player_id}', notifications.WARNING))

    try: # get data before main command
        data = await handle(GetNotificationDataFromTeamTransfersCommand(body.invite_id))
        user_ids = await handle(GetTeamManagerAndLeaderUserIdsCommand(data.team_id))
    except Exception:
        pass

    command = DeclineInviteCommand(body.invite_id, request.state.user.player_id)
    await handle(command)
    return JSONResponse({}, background=BackgroundTask(notify))

@bind_request_body(LeaveRosterRequestData)
@require_logged_in
async def leave_team(request: Request, body: LeaveRosterRequestData) -> JSONResponse:
    async def notify():
        player_id = request.state.user.player_id
        player_name = await handle(GetPlayerNameCommand(player_id,))
        data = await handle(GetNotificationTeamRosterDataCommand(body.roster_id))
        user_ids = await handle(GetTeamManagerAndLeaderUserIdsCommand(data.team_id))
        content_args = {'player_name': player_name, 'roster_name': data.roster_name or data.team_name}
        await handle(DispatchNotificationCommand(user_ids, notifications.TEAM_PLAYER_LEFT , content_args, f'/registry/players/profile?id={player_id}', notifications.WARNING))

    command = LeaveRosterCommand(request.state.user.player_id, body.roster_id)
    await handle(command)
    return JSONResponse({}, background=BackgroundTask(notify))

@bind_request_body(ApproveTransferRequestData)
@require_permission(permissions.MANAGE_TRANSFERS)
async def approve_transfer(request: Request, body: ApproveTransferRequestData) -> JSONResponse:
    async def notify():
        data = await handle(GetNotificationDataFromTeamTransfersCommand(body.invite_id))
        user_ids = await handle(GetTeamManagerAndLeaderUserIdsCommand(data.team_id))
        player_user_id = await handle(GetUserIdFromPlayerIdCommand(data.player_id))
        if player_user_id is not None:
            content_args = {'roster_name': data.roster_name or data.team_name}
            await handle(DispatchNotificationCommand([player_user_id], notifications.STAFF_APPROVE_TRANSFER, content_args, f'/registry/teams/profile?id={data.team_id}', notifications.SUCCESS))
        content_args = {'player_name': data.player_name, 'roster_name': data.roster_name or data.team_name}
        await handle(DispatchNotificationCommand(user_ids, notifications.TEAM_TRANSFER_ACCEPTED , content_args, f'/registry/players/profile?id={data.team_id}', notifications.SUCCESS))

    command = ApproveTransferCommand(body.invite_id)
    await handle(command)
    return JSONResponse({}, background=BackgroundTask(notify))

@bind_request_body(DenyTransferRequestData)
@require_permission(permissions.MANAGE_TRANSFERS)
async def deny_transfer(request: Request, body: DenyTransferRequestData) -> JSONResponse:
    async def notify():
        data = await handle(GetNotificationDataFromTeamTransfersCommand(body.invite_id))
        user_ids = await handle(GetTeamManagerAndLeaderUserIdsCommand(data.team_id))
        player_user_id = await handle(GetUserIdFromPlayerIdCommand(data.player_id))
        if player_user_id is not None:
            content_args = {'roster_name': data.roster_name or data.team_name}
            await handle(DispatchNotificationCommand([player_user_id], notifications.STAFF_DENY_TRANSFER, content_args, f'/registry/teams/profile?id={data.team_id}', notifications.WARNING))
        content_args = {'player_name': data.player_name, 'roster_name': data.roster_name or data.team_name}
        await handle(DispatchNotificationCommand(user_ids, notifications.TEAM_TRANSFER_DENIED , content_args, f'/registry/players/profile?id={data.player_id}', notifications.WARNING))

    command = DenyTransferCommand(body.invite_id, body.send_back)
    await handle(command)
    return JSONResponse({}, background=BackgroundTask(notify))

@bind_request_query(TransferFilter)
async def view_approved_transfers(request: Request, filter: TransferFilter) -> JSONResponse:
    command = ViewTransfersCommand(filter, "approved")
    transfers = await handle(command)
    return JSONResponse(transfers)

@bind_request_query(TransferFilter)
@require_permission(permissions.MANAGE_TRANSFERS)
async def view_pending_transfers(request: Request, filter: TransferFilter) -> JSONResponse:
    command = ViewTransfersCommand(filter, "pending")
    transfers = await handle(command)
    return JSONResponse(transfers)

@bind_request_query(TransferFilter)
@require_permission(permissions.MANAGE_TRANSFERS)
async def view_denied_transfers(request: Request, filter: TransferFilter) -> JSONResponse:
    command = ViewTransfersCommand(filter, "denied")
    transfers = await handle(command)
    return JSONResponse(transfers)

@bind_request_query(RosterEditFilter)
@require_permission(permissions.MANAGE_TEAMS)
async def list_roster_edit_requests(request: Request, filter: RosterEditFilter) -> JSONResponse:
    command = ListRosterEditRequestsCommand(filter)
    requests = await handle(command)
    return JSONResponse(requests)

@bind_request_body(ForceTransferPlayerRequestData)
@require_permission(permissions.MANAGE_TEAMS)
async def force_transfer_player(request: Request, body: ForceTransferPlayerRequestData) -> JSONResponse:
    async def notify():
        player_name = await handle(GetPlayerNameCommand(body.player_id))
        data = await handle(GetNotificationTeamRosterDataCommand(body.roster_id))
        user_ids = await handle(GetTeamManagerAndLeaderUserIdsCommand(body.team_id))
        content_args = {'player_name': player_name, 'roster_name': data.roster_name or data.team_name}
        await handle(DispatchNotificationCommand(user_ids, notifications.TEAM_TRANSFER_ACCEPTED , content_args, f'/registry/players/profile?id={body.player_id}', notifications.SUCCESS))

    command = ForceTransferPlayerCommand(body.player_id, body.roster_id, body.team_id, body.roster_leave_id, body.is_bagger_clause)
    await handle(command)
    return JSONResponse({}, background=BackgroundTask(notify))

@bind_request_body(EditTeamMemberInfoRequestData)
@require_permission(permissions.MANAGE_TEAMS)
async def edit_team_member_info(request: Request, body: EditTeamMemberInfoRequestData) -> JSONResponse:
    command = EditTeamMemberCommand(body.player_id, body.roster_id, body.team_id, body.join_date, body.leave_date, body.is_bagger_clause)
    await handle(command)
    return JSONResponse({})

@bind_request_body(KickPlayerRequestData)
@require_team_permission(team_permissions.MANAGE_ROSTERS)
async def kick_player(request: Request, body: KickPlayerRequestData) -> JSONResponse:
    async def notify():
        user_id = await handle(GetUserIdFromPlayerIdCommand(body.player_id))
        if user_id is None:
            return
        data = await handle(GetNotificationTeamRosterDataCommand(body.roster_id))
        content_args = {'roster_name': data.roster_name or data.team_name}
        await handle(DispatchNotificationCommand([user_id], notifications.TEAM_KICKED , content_args, f'/registry/teams/profile?id={body.team_id}', notifications.WARNING))

    timestamp = int(datetime.now(timezone.utc).timestamp())
    command = EditTeamMemberCommand(body.player_id, body.roster_id, body.team_id, None, timestamp, None)
    await handle(command)
    return JSONResponse({}, background=BackgroundTask(notify))

@bind_request_body(KickPlayerRequestData)
@require_permission(permissions.MANAGE_TEAMS)
async def mod_kick_player(request: Request, body: KickPlayerRequestData) -> JSONResponse:
    async def notify():
        user_id = await handle(GetUserIdFromPlayerIdCommand(body.player_id))
        if user_id is None:
            return
        player_name = await handle(GetPlayerNameCommand(body.player_id))
        data = await handle(GetNotificationTeamRosterDataCommand(body.roster_id))
        team_leader_ids = await handle(GetTeamManagerAndLeaderUserIdsCommand(body.team_id))
        content_args = {'roster_name': data.roster_name or data.team_name}
        await handle(DispatchNotificationCommand([user_id], notifications.TEAM_KICKED , content_args, f'/registry/teams/profile?id={body.team_id}', notifications.WARNING))
        content_args = {'player_name': player_name, 'team_name': data.team_name}
        await handle(DispatchNotificationCommand(team_leader_ids, notifications.STAFF_KICK_PLAYER, content_args, f'/registry/teams/profile?id={body.team_id}', notifications.WARNING))

    timestamp = int(datetime.now(timezone.utc).timestamp())
    command = EditTeamMemberCommand(body.player_id, body.roster_id, body.team_id, None, timestamp, None)
    await handle(command)
    return JSONResponse({}, background=BackgroundTask(notify))

@bind_request_query(TeamFilter)
async def list_teams(request: Request, body: TeamFilter) -> JSONResponse:
    command = ListTeamsCommand(body)
    teams = await handle(command)
    return JSONResponse(teams)

@bind_request_query(TeamFilter)
@require_permission(permissions.MANAGE_TEAMS)
async def list_pending_teams(request: Request, body: TeamFilter) -> JSONResponse:
    command = ListTeamsCommand(body, approval_status="pending")
    teams = await handle(command)
    return JSONResponse(teams)

@bind_request_query(TeamFilter)
@require_permission(permissions.MANAGE_TEAMS)
async def list_denied_teams(request: Request, body: TeamFilter) -> JSONResponse:
    command = ListTeamsCommand(body, approval_status="denied")
    teams = await handle(command)
    return JSONResponse(teams)

@require_permission(permissions.MANAGE_TEAMS)
async def list_unapproved_rosters(request: Request) -> JSONResponse:
    command = ListRostersCommand(approved=False)
    rosters = await handle(command)
    return JSONResponse(rosters)

@require_permission(permissions.MANAGE_TEAMS)
async def approve_roster(request: Request) -> JSONResponse:
    async def notify():
        user_ids = await handle(GetTeamManagerAndLeaderUserIdsCommand(team_id))
        data = await handle(GetNotificationTeamRosterDataCommand(roster_id))
        content_args = {'roster_name': data.roster_name or data.team_name}
        await handle(DispatchNotificationCommand(user_ids, notifications.ROSTER_APPROVED , content_args, f'/registry/teams/profile?id={team_id}', notifications.SUCCESS))

    team_id = request.path_params['team_id']
    roster_id = request.path_params['rosterId']
    command = ApproveRosterCommand(team_id, roster_id)
    await handle(command)
    return JSONResponse({}, background=BackgroundTask(notify))

@require_permission(permissions.MANAGE_TEAMS)
async def deny_roster(request: Request) -> JSONResponse:
    async def notify():
        user_ids = await handle(GetTeamManagerAndLeaderUserIdsCommand(team_id))
        data = await handle(GetNotificationTeamRosterDataCommand(roster_id))
        content_args = {'roster_name': data.roster_name or data.team_name}
        await handle(DispatchNotificationCommand(user_ids, notifications.ROSTER_DENIED , content_args, f'/registry/teams/profile?id={team_id}', notifications.WARNING))

    team_id = request.path_params['team_id']
    roster_id = request.path_params['rosterId']
    command = DenyRosterCommand(team_id, roster_id)
    await handle(command)
    return JSONResponse({}, background=BackgroundTask(notify))

@bind_request_query(RegisterableRostersRequestData)
@require_logged_in
async def list_registerable_rosters(request: Request, body: RegisterableRostersRequestData) -> JSONResponse:
    user = request.state.user.id
    command = GetRegisterableRostersCommand(user, body.tournament_id, body.game, body.mode)
    rosters = await handle(command)
    return JSONResponse(rosters)

async def team_edit_history(request: Request) -> JSONResponse:
    team_id = request.path_params['team_id']
    command = ViewTeamEditHistoryCommand(team_id)
    edits = await handle(command)
    return JSONResponse(edits)

async def roster_edit_history(request: Request) -> JSONResponse:
    team_id = request.path_params['team_id']
    roster_id = request.path_params['rosterId']
    command = ViewRosterEditHistoryCommand(team_id, roster_id)
    edits = await handle(command)
    return JSONResponse(edits)

@bind_request_body(MergeTeamsRequestData)
@require_permission(permissions.MERGE_TEAMS)
async def merge_teams(request: Request, body: MergeTeamsRequestData) -> JSONResponse:
    await handle(MergeTeamsCommand(body.from_team_id, body.to_team_id))
    return JSONResponse({})


routes: list[Route] = [
    Route('/api/registry/teams/create', create_team, methods=['POST']),
    Route('/api/registry/teams/request', request_create_team, methods=['POST']),
    Route('/api/registry/teams/{team_id:int}', view_team),
    Route('/api/registry/teams/forceEdit', edit_team, methods=['POST']), # dispatches notification
    Route('/api/registry/teams/edit', manager_edit_team, methods=['POST']),
    Route('/api/registry/teams/{team_id:int}/approve', approve_team, methods=['POST']), # dispatches notification
    Route('/api/registry/teams/{team_id:int}/deny', deny_team, methods=['POST']), # dispatches notification
    Route('/api/registry/teams/requestChange', request_edit_team, methods=['POST']),
    Route('/api/registry/teams/approveChange', approve_team_edit_request, methods=['POST']), # dispatches notification
    Route('/api/registry/teams/denyChange', deny_team_edit_request, methods=['POST']), # dispatches notification
    Route('/api/registry/teams/changeRequests', list_team_edit_requests),
    Route('/api/registry/teams/createRoster', create_roster, methods=['POST']),
    Route('/api/registry/teams/requestCreateRoster', request_create_roster, methods=['POST']),
    Route('/api/registry/teams/forceEditRoster', edit_roster, methods=['POST']), # dispatches notification
    Route('/api/registry/teams/editRoster', manager_edit_roster, methods=['POST']),
    Route('/api/registry/teams/requestRosterChange', request_edit_roster, methods=['POST']),
    Route('/api/registry/teams/approveRosterChange', approve_roster_edit_request, methods=['POST']), # dispatches notification
    Route('/api/registry/teams/denyRosterChange', deny_roster_edit_request, methods=['POST']), # dispatches notification
    Route('/api/registry/teams/invitePlayer', invite_player, methods=['POST']), # dispatches notification
    Route('/api/registry/teams/deleteInvite', delete_invite, methods=['POST']),
    Route('/api/registry/teams/forceDeleteInvite', mod_delete_invite, methods=['POST']),
    Route('/api/registry/teams/acceptInvite', accept_invite, methods=['POST']), # dispatches notification
    Route('/api/registry/teams/declineInvite', decline_invite, methods=['POST']), # dispatches notification
    Route('/api/registry/teams/leave', leave_team, methods=['POST']), # dispatches notification
    Route('/api/registry/teams/approveTransfer', approve_transfer, methods=['POST']), # dispatches notification
    Route('/api/registry/teams/denyTransfer', deny_transfer, methods=['POST']), # dispatches notification
    Route('/api/registry/teams/transfers/approved', view_approved_transfers),
    Route('/api/registry/teams/transfers/pending', view_pending_transfers),
    Route('/api/registry/teams/transfers/denied', view_denied_transfers),
    Route('/api/registry/teams/rosterChangeRequests', list_roster_edit_requests),
    Route('/api/registry/teams/forceTransferPlayer', force_transfer_player, methods=['POST']), # dispatches notification
    Route('/api/registry/teams/editTeamMemberInfo', edit_team_member_info, methods=['POST']),
    Route('/api/registry/teams/kickPlayer', kick_player, methods=['POST']), # dispatches notification
    Route('/api/registry/teams/forceKickPlayer', mod_kick_player, methods=['POST']), # dispatches notification
    Route('/api/registry/teams', list_teams),
    Route('/api/registry/teams/pendingTeams', list_pending_teams),
    Route('/api/registry/teams/deniedTeams', list_denied_teams),
    Route('/api/registry/teams/unapprovedRosters', list_unapproved_rosters),
    Route('/api/registry/teams/{team_id:int}/approveRoster/{rosterId:int}', approve_roster, methods=['POST']), # dispatches notification
    Route('/api/registry/teams/{team_id:int}/denyRoster/{rosterId:int}', deny_roster, methods=['POST']), # dispatches notification
    Route('/api/registry/teams/getRegisterable', list_registerable_rosters),
    Route('/api/registry/teams/{team_id:int}/editRequests', team_edit_history),
    Route('/api/registry/teams/{team_id:int}/rosterEditRequests/{rosterId:int}', roster_edit_history),
    Route('/api/registry/teams/merge', merge_teams, methods=['POST']),
]