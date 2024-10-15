from starlette.requests import Request
from starlette.routing import Route
from api.auth import require_permission, require_team_permission, require_series_permission, require_tournament_permission
from api.data import handle
from api.utils.responses import JSONResponse, bind_request_body
from common.auth import permissions
from common.data.commands import *
from common.data.models import *
import common.data.notifications as notifications

@require_permission(permissions.MANAGE_USER_ROLES)
async def list_roles(request: Request) -> JSONResponse:
    roles = await handle(ListRolesCommand())
    return JSONResponse(roles)

@require_permission(permissions.MANAGE_USER_ROLES)
async def role_info(request: Request) -> JSONResponse:
    role_id = request.path_params['role_id']
    role_info = await handle(GetRoleInfoCommand(role_id))
    return JSONResponse(role_info)

@bind_request_body(GrantRoleRequestData)
@require_permission(permissions.MANAGE_USER_ROLES)
async def grant_role_to_player(request: Request, body: GrantRoleRequestData) -> JSONResponse:
    user_id = request.state.user.id
    command = GrantRoleCommand(user_id, body.player_id, body.role_name, body.expires_on)
    await handle(command)
    if body.role_name != BANNED:
        user_id = await handle(GetFieldFromTableCommand("SELECT id FROM users WHERE player_id = ?", (body.player_id,)))
        await handle(DispatchNotificationCommand([int(user_id)], notifications.ROLE_ADD, [body.role_name], f'/registry/players/profile?id={body.player_id}', notifications.INFO))
    return JSONResponse({})

@bind_request_body(RemoveRoleRequestData)
@require_permission(permissions.MANAGE_USER_ROLES)
async def remove_role_from_player(request: Request, body: RemoveRoleRequestData) -> JSONResponse:
    user_id = request.state.user.id
    command = RemoveRoleCommand(user_id, body.player_id, body.role_name)
    await handle(command)
    if body.role_name != BANNED:
        user_id = await handle(GetFieldFromTableCommand("SELECT id FROM users WHERE player_id = ?", (body.player_id,)))
        await handle(DispatchNotificationCommand([int(user_id)], notifications.ROLE_REMOVE, [body.role_name], f'/registry/players/profile?id={body.player_id}', notifications.WARNING))
    return JSONResponse({})

async def list_team_roles(request: Request) -> JSONResponse:
    roles = await handle(ListTeamRolesCommand())
    return JSONResponse(roles)

@require_team_permission(team_permissions.MANAGE_TEAM_ROLES)
async def team_role_info(request: Request) -> JSONResponse:
    role_id = request.path_params['role_id']
    team_id = request.path_params['team_id']
    role_info = await handle(GetTeamRoleInfoCommand(role_id, team_id))
    return JSONResponse(role_info)

@bind_request_body(GrantRoleRequestData)
@require_team_permission(team_permissions.MANAGE_TEAM_ROLES)
async def grant_team_role_to_player(request: Request, body: GrantRoleRequestData) -> JSONResponse:
    user_id = request.state.user.id
    team_id = request.path_params['team_id']
    command = GrantTeamRoleCommand(user_id, body.player_id, team_id, body.role_name, body.expires_on)
    await handle(command)
    uid = await handle(GetFieldFromTableCommand("SELECT id FROM users WHERE player_id = ?", (body.player_id,)))
    team_name = await handle(GetFieldFromTableCommand("SELECT name FROM teams WHERE id = ?", (team_id,)))
    await handle(DispatchNotificationCommand([int(uid)], notifications.TEAM_ROLE_ADD, [body.role_name, team_name], f'/registry/teams/profile?id={team_id}', notifications.INFO))
    return JSONResponse({})

@bind_request_body(RemoveRoleRequestData)
@require_team_permission(team_permissions.MANAGE_TEAM_ROLES)
async def remove_team_role_from_player(request: Request, body: RemoveRoleRequestData) -> JSONResponse:
    user_id = request.state.user.id
    team_id = request.path_params['team_id']
    command = RemoveTeamRoleCommand(user_id, body.player_id, team_id, body.role_name)
    await handle(command)
    uid = await handle(GetFieldFromTableCommand("SELECT id FROM users WHERE player_id = ?", (body.player_id,)))
    team_name = await handle(GetFieldFromTableCommand("SELECT name FROM teams WHERE id = ?", (team_id,)))
    await handle(DispatchNotificationCommand([int(uid)], notifications.TEAM_ROLE_REMOVE, [body.role_name, team_name], f'/registry/teams/profile?id={team_id}', notifications.WARNING))
    return JSONResponse({})

async def list_series_roles(request: Request) -> JSONResponse:
    roles = await handle(ListSeriesRolesCommand())
    return JSONResponse(roles)

@require_series_permission(series_permissions.MANAGE_SERIES_ROLES)
async def series_role_info(request: Request) -> JSONResponse:
    role_id = request.path_params['role_id']
    series_id = request.path_params['series_id']
    role_info = await handle(GetSeriesRoleInfoCommand(role_id, series_id))
    return JSONResponse(role_info)

@bind_request_body(GrantRoleRequestData)
@require_series_permission(series_permissions.MANAGE_SERIES_ROLES)
async def grant_series_role_to_player(request: Request, body: GrantRoleRequestData) -> JSONResponse:
    user_id = request.state.user.id
    series_id = request.path_params['series_id']
    command = GrantSeriesRoleCommand(user_id, body.player_id, series_id, body.role_name, body.expires_on)
    await handle(command)
    uid = await handle(GetFieldFromTableCommand("SELECT id FROM users WHERE player_id = ?", (body.player_id,)))
    series_name, series_id = await handle(GetRowFromTableCommand("SELECT name, id FROM tournament_series WHERE id = ?", (series_id,)))
    await handle(DispatchNotificationCommand([int(uid)], notifications.SERIES_ROLE_ADD, [body.role_name, series_name], f'/tournaments/series/details?id={series_id}', notifications.INFO))
    return JSONResponse({})

@bind_request_body(RemoveRoleRequestData)
@require_series_permission(series_permissions.MANAGE_SERIES_ROLES)
async def remove_series_role_from_player(request: Request, body: RemoveRoleRequestData) -> JSONResponse:
    user_id = request.state.user.id
    series_id = request.path_params['series_id']
    command = RemoveSeriesRoleCommand(user_id, body.player_id, series_id, body.role_name)
    await handle(command)
    uid = await handle(GetFieldFromTableCommand("SELECT id FROM users WHERE player_id = ?", (body.player_id,)))
    series_name, series_id = await handle(GetRowFromTableCommand("SELECT name, id FROM tournament_series WHERE id = ?", (series_id,)))
    await handle(DispatchNotificationCommand([int(uid)], notifications.SERIES_ROLE_REMOVE, [body.role_name, series_name], f'/tournaments/series/details?id={series_id}', notifications.WARNING))
    return JSONResponse({})

async def list_tournament_roles(request: Request) -> JSONResponse:
    roles = await handle(ListTournamentRolesCommand())
    return JSONResponse(roles)

@require_tournament_permission(tournament_permissions.MANAGE_TOURNAMENT_ROLES)
async def tournament_role_info(request: Request) -> JSONResponse:
    role_id = request.path_params['role_id']
    tournament_id = request.path_params['tournament_id']
    role_info = await handle(GetTournamentRoleInfoCommand(role_id, tournament_id))
    return JSONResponse(role_info)

@bind_request_body(GrantRoleRequestData)
@require_tournament_permission(tournament_permissions.MANAGE_TOURNAMENT_ROLES)
async def grant_tournament_role_to_player(request: Request, body: GrantRoleRequestData) -> JSONResponse:
    user_id = request.state.user.id
    tournament_id = request.path_params['tournament_id']
    command = GrantTournamentRoleCommand(user_id, body.player_id, tournament_id, body.role_name, body.expires_on)
    await handle(command)
    uid = await handle(GetFieldFromTableCommand("SELECT id FROM users WHERE player_id = ?", (body.player_id,)))
    tournament_name = await handle(GetFieldFromTableCommand("SELECT name FROM tournaments WHERE id = ?", (tournament_id,)))
    await handle(DispatchNotificationCommand([int(uid)], notifications.TOURNAMENT_ROLE_ADD, [body.role_name, tournament_name], f'/tournaments/details?id={tournament_id}', notifications.INFO))
    return JSONResponse({})

@bind_request_body(RemoveRoleRequestData)
@require_tournament_permission(tournament_permissions.MANAGE_TOURNAMENT_ROLES)
async def remove_tournament_role_from_player(request: Request, body: RemoveRoleRequestData) -> JSONResponse:
    user_id = request.state.user.id
    tournament_id = request.path_params['tournament_id']
    command = RemoveTournamentRoleCommand(user_id, body.player_id, tournament_id, body.role_name)
    await handle(command)
    uid = await handle(GetFieldFromTableCommand("SELECT id FROM users WHERE player_id = ?", (body.player_id,)))
    tournament_name = await handle(GetFieldFromTableCommand("SELECT name FROM tournaments WHERE id = ?", (tournament_id,)))
    await handle(DispatchNotificationCommand([int(uid)], notifications.TOURNAMENT_ROLE_ADD, [body.role_name, tournament_name], f'/tournaments/details?id={tournament_id}', notifications.WARNING))
    return JSONResponse({})

routes = [
    Route('/api/roles', list_roles),
    Route('/api/roles/{role_id:int}', role_info),
    Route('/api/roles/grant', grant_role_to_player, methods=['POST']),
    Route('/api/roles/remove', remove_role_from_player, methods=['POST']),
    Route('/api/registry/teams/roles', list_team_roles),
    Route('/api/registry/teams/{team_id:int}/roles/{role_id:int}', team_role_info),
    Route('/api/registry/teams/{team_id:int}/roles/grant', grant_team_role_to_player, methods=['POST']),
    Route('/api/registry/teams/{team_id:int}/roles/remove', remove_team_role_from_player, methods=['POST']),
    Route('/api/tournaments/series/roles', list_series_roles),
    Route('/api/tournaments/series/{series_id:int}/roles/{role_id:int}', series_role_info),
    Route('/api/tournaments/series/{series_id:int}/roles/grant', grant_series_role_to_player, methods=['POST']),
    Route('/api/tournaments/series/{series_id:int}/roles/remove', remove_series_role_from_player, methods=['POST']),
    Route('/api/tournaments/roles', list_tournament_roles),
    Route('/api/tournaments/{tournament_id:int}/roles/{role_id:int}', tournament_role_info),
    Route('/api/tournaments/{tournament_id:int}/roles/grant', grant_tournament_role_to_player, methods=['POST']),
    Route('/api/tournaments/{tournament_id:int}/roles/remove', remove_tournament_role_from_player, methods=['POST'])
]
