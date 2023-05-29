from starlette.requests import Request
from starlette.routing import Route
from api.auth import require_permission, require_logged_in, require_team_permission
from api.data import handle
from datetime import datetime
from api.utils.responses import JSONResponse, bind_request_body
from common.auth import permissions
from common.data.commands import *
from common.data.models import *

# for moderator use, does not go to approval queue
@bind_request_body(CreateTeamRequestData)
@require_permission(permissions.MANAGE_TEAMS)
async def create_team(request: Request, body: CreateTeamRequestData) -> JSONResponse:
    command = CreateTeamCommand(body.name, body.tag, body.description, body.language, body.color,
        body.logo, body.approval_status, body.is_historical, body.game, body.mode, body.is_recruiting, body.is_active, True)
    await handle(command)
    return JSONResponse({})

@bind_request_body(RequestCreateTeamRequestData)
async def request_create_team(request: Request, body: RequestCreateTeamRequestData) -> JSONResponse:
    approval_status = "pending"
    command = CreateTeamCommand(body.name, body.tag, body.description, body.language, body.color,
                                body.logo, approval_status, False, body.game, body.mode, body.is_recruiting, True, False)
    await handle(command)
    return JSONResponse({})

async def view_team(request: Request) -> JSONResponse:
    team_id = request.path_params['id']
    command = GetTeamInfoCommand(team_id)
    team = await handle(command)
    return JSONResponse(team)

# for moderator use, allows for direct editing of name/tags and approving/disapproving teams
@bind_request_body(EditTeamRequestData)
@require_permission(permissions.MANAGE_TEAMS)
async def edit_team(request: Request, body: EditTeamRequestData) -> JSONResponse:
    command = EditTeamCommand(body.team_id, body.name, body.tag, body.description, body.language, body.color,
        body.logo, body.approval_status, body.is_historical, True)
    await handle(command)
    return JSONResponse({})

# for editing non-essential team info such as description, color, etc
@bind_request_body(ManagerEditTeamRequestData)
@require_team_permission(permissions.EDIT_TEAM_INFO)
async def manager_edit_team(request: Request, body: ManagerEditTeamRequestData) -> JSONResponse:
    command = ManagerEditTeamCommand(body.team_id, body.description, body.language, body.color, body.logo)
    await handle(command)
    return JSONResponse({})

# for editing team name/tag, which requires moderator approval
@bind_request_body(RequestEditTeamRequestData)
@require_team_permission(permissions.EDIT_TEAM_INFO)
async def request_edit_team(request: Request, body: RequestEditTeamRequestData) -> JSONResponse:
    command = RequestEditTeamCommand(body.team_id, body.name, body.tag)
    await handle(command)
    return JSONResponse({})

@bind_request_body(ApproveTeamEditRequestData)
@require_permission(permissions.MANAGE_TEAMS)
async def approve_team_edit_request(request: Request, body: ApproveTeamEditRequestData) -> JSONResponse:
    command = ApproveTeamEditCommand(body.request_id)
    await handle(command)
    return JSONResponse({})

@bind_request_body(DenyTeamEditRequestData)
@require_permission(permissions.MANAGE_TEAMS)
async def deny_team_edit_request(request: Request, body: DenyTeamEditRequestData) -> JSONResponse:
    command = DenyTeamEditCommand(body.request_id)
    await handle(command)
    return JSONResponse({})

# for moderator use, does not go to approval queue
@bind_request_body(CreateRosterRequestData)
@require_permission(permissions.MANAGE_TEAMS)
async def create_roster(request: Request, body: CreateRosterRequestData) -> JSONResponse:
    command = CreateRosterCommand(body.team_id, body.game, body.mode, body.name, body.tag, body.is_recruiting, body.is_active, body.approval_status)
    await handle(command)
    return JSONResponse({})

# for moderator use, allows for direct editing of name/tags
@bind_request_body(EditRosterRequestData)
@require_permission(permissions.MANAGE_TEAMS)
async def edit_roster(request: Request, body: EditRosterRequestData) -> JSONResponse:
    command = EditRosterCommand(body.roster_id, body.team_id, body.name, body.tag, body.is_recruiting,
                                body.is_active, body.approval_status)
    await handle(command)
    return JSONResponse({})

@bind_request_body(InviteRosterPlayerRequestData)
@require_team_permission(permissions.INVITE_TEAM_PLAYERS)
async def invite_player(request: Request, body: InviteRosterPlayerRequestData) -> JSONResponse:
    command = InvitePlayerCommand(body.player_id, body.roster_id, body.team_id)
    await handle(command)
    return JSONResponse({})

@bind_request_body(InviteRosterPlayerRequestData)
@require_team_permission(permissions.INVITE_TEAM_PLAYERS)
async def delete_invite(request: Request, body: InviteRosterPlayerRequestData) -> JSONResponse:
    command = DeleteInviteCommand(body.player_id, body.roster_id, body.team_id)
    await handle(command)
    return JSONResponse({})

@bind_request_body(AcceptRosterInviteRequestData)
@require_logged_in
async def accept_invite(request: Request, body: AcceptRosterInviteRequestData) -> JSONResponse:
    command = AcceptInviteCommand(body.invite_id, body.roster_leave_id, request.state.user.player_id)
    await handle(command)
    return JSONResponse({})

@bind_request_body(DeclineRosterInviteRequestData)
@require_logged_in
async def decline_invite(request: Request, body: DeclineRosterInviteRequestData) -> JSONResponse:
    command = DeclineInviteCommand(body.invite_id, request.state.user.player_id)
    await handle(command)
    return JSONResponse({})

@bind_request_body(LeaveRosterRequestData)
@require_logged_in
async def leave_team(request: Request, body: LeaveRosterRequestData) -> JSONResponse:
    command = LeaveRosterCommand(request.state.user.player_id, body.roster_id)
    await handle(command)
    return JSONResponse({})

@bind_request_body(ApproveTransferRequestData)
@require_permission(permissions.MANAGE_TRANSFERS)
async def approve_transfer(request: Request, body: ApproveTransferRequestData) -> JSONResponse:
    command = ApproveTransferCommand(body.invite_id)
    await handle(command)
    return JSONResponse({})

@bind_request_body(DenyTransferRequestData)
@require_permission(permissions.MANAGE_TRANSFERS)
async def deny_transfer(request: Request, body: DenyTransferRequestData) -> JSONResponse:
    command = DenyTransferCommand(body.invite_id, body.send_back)
    await handle(command)
    return JSONResponse({})

@bind_request_body(RequestEditRosterRequestData)
@require_team_permission(permissions.EDIT_TEAM_INFO)
async def request_edit_roster(request: Request, body: RequestEditRosterRequestData) -> JSONResponse:
    command = RequestEditRosterCommand(body.roster_id, body.team_id, body.name, body.tag)
    await handle(command)
    return JSONResponse({})

@bind_request_body(ApproveRosterEditRequestData)
@require_permission(permissions.MANAGE_TEAMS)
async def approve_roster_edit_request(request: Request, body: ApproveRosterEditRequestData) -> JSONResponse:
    command = ApproveRosterEditCommand(body.request_id)
    await handle(command)
    return JSONResponse({})

@bind_request_body(DenyRosterEditRequestData)
@require_permission(permissions.MANAGE_TEAMS)
async def deny_roster_edit_request(request: Request, body: DenyRosterEditRequestData) -> JSONResponse:
    command = DenyRosterEditCommand(body.request_id)
    await handle(command)
    return JSONResponse({})

@bind_request_body(ForceTransferPlayerRequestData)
@require_permission(permissions.MANAGE_TEAM_ROSTERS)
async def force_transfer_player(request: Request, body: ForceTransferPlayerRequestData) -> JSONResponse:
    command = ForceTransferPlayerCommand(body.player_id, body.roster_id, body.team_id, body.roster_leave_id)
    await handle(command)
    return JSONResponse({})

@bind_request_body(EditTeamMemberInfoRequestData)
@require_permission(permissions.MANAGE_TEAM_ROSTERS)
async def edit_team_member_info(request: Request, body: EditTeamMemberInfoRequestData) -> JSONResponse:
    command = EditTeamMemberCommand(body.id, body.roster_id, body.team_id, body.join_date, body.leave_date)
    await handle(command)
    return JSONResponse({})

@bind_request_body(KickPlayerRequestData)
@require_team_permission(permissions.MANAGE_TEAM_ROSTERS)
async def kick_player(request: Request, body: KickPlayerRequestData) -> JSONResponse:
    timestamp = int(datetime.utcnow().timestamp())
    command = EditTeamMemberCommand(body.id, body.roster_id, body.team_id, None, timestamp)
    await handle(command)
    return JSONResponse({})

#todo: endpoints for giving team roles

routes: list[Route] = [
    Route('/api/registry/teams/create', create_team, methods=['POST']),
    Route('/api/registry/teams/{id:int}', view_team),
    Route('/api/registry/teams/forceEdit', edit_team, methods=['POST']),
    Route('/api/registry/teams/edit', manager_edit_team, methods=['POST']),
    Route('/api/registry/teams/requestChange', request_edit_team, methods=['POST']),
    Route('/api/registry/teams/approveChange', approve_team_edit_request, methods=['POST']),
    Route('/api/registry/teams/denyChange', deny_team_edit_request, methods=['POST']),
    Route('/api/registry/teams/createRoster', create_roster, methods=['POST']),
    Route('/api/registry/teams/editRoster', edit_roster, methods=['POST']),
    Route('/api/registry/teams/invitePlayer', invite_player, methods=['POST']),
    Route('/api/registry/teams/deleteInvite', delete_invite, methods=['POST']),
    Route('/api/registry/teams/acceptInvite', accept_invite, methods=['POST']),
    Route('/api/registry/teams/declineInvite', decline_invite, methods=['POST']),
    Route('/api/registry/teams/leave', leave_team, methods=['POST']),
    Route('/api/registry/teams/approveTransfer', approve_transfer, methods=['POST']),
    Route('/api/registry/teams/requestRosterChange', request_edit_roster, methods=['POST']),
    Route('/api/registry/teams/approveRosterChange', approve_roster_edit_request, methods=['POST']),
    Route('/api/registry/teams/denyRosterChange', deny_roster_edit_request, methods=['POST']),
    Route('/api/registry/teams/forceTransferPlayer', force_transfer_player, methods=['POST']),
    Route('/api/registry/teams/editTeamMemberInfo', edit_team_member_info, methods=['POST']),
    Route('/api/registry/teams/kickPlayer', kick_player, methods=['POST'])
]