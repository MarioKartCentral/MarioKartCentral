from starlette.requests import Request
from starlette.routing import Route
from api.auth import require_permission, require_logged_in, require_team_permission
from api.data import handle
from api.utils.responses import JSONResponse, bind_request_body
from common.auth import permissions
from common.data.commands import (CreateTeamCommand, EditRosterCommand, GetTeamInfoCommand, EditTeamCommand, CreateRosterCommand, InvitePlayerCommand, AcceptInviteCommand, DeclineInviteCommand,
                                  DeleteInviteCommand, ManagerEditTeamCommand, RequestEditTeamCommand, LeaveRosterCommand, ApproveTransferCommand)
from common.data.models import (CreateTeamRequestData, EditTeamRequestData, CreateRosterRequestData, EditRosterRequestData, InviteRosterPlayerRequestData, AcceptRosterInviteRequestData, 
                                DeclineRosterInviteRequestData, RequestCreateTeamRequestData, ManagerEditTeamRequestData, RequestEditTeamRequestData, LeaveRosterRequestData,
                                ApproveTransferRequestData)

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

#todo: endpoints for giving team roles and editing registration history,
#       approve/deny team edit requests, create roster edit requests,
#       approve/deny roster edit requests, force add player to roster,
#       force remove player from roster.

#additional:    need to automatically handle adding/removing players from squad rosters whenever
#               their new team is linked to the roster. maybe players can just select which squads
#               to join upon accepting the transfer or something like that.
#               also, add/edit/remove FC endpoints

routes: list[Route] = [
    Route('/api/registry/teams/create', create_team, methods=['POST']),
    Route('/api/registry/teams/{id:int}', view_team),
    Route('/api/registry/teams/forceEdit', edit_team, methods=['POST']),
    Route('/api/registry/teams/edit', manager_edit_team, methods=['POST']),
    Route('/api/registry/teams/requestChange', request_edit_team, methods=['POST']),
    Route('/api/registry/teams/createRoster', create_roster, methods=['POST']),
    Route('/api/registry/teams/editRoster', edit_roster, methods=['POST']),
    Route('/api/registry/teams/invitePlayer', invite_player, methods=['POST']),
    Route('/api/registry/teams/deleteInvite', delete_invite, methods=['POST']),
    Route('/api/registry/teams/acceptInvite', accept_invite, methods=['POST']),
    Route('/api/registry/teams/declineInvite', decline_invite, methods=['POST']),
    Route('/api/registry/teams/leave', leave_team, methods=['POST']),
    Route('/api/registry/teams/approveTransfer', approve_transfer, methods=['POST'])
]