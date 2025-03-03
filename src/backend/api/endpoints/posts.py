from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from api.utils.responses import JSONResponse, bind_request_body, bind_request_query
from api.auth import require_permission, require_series_permission, require_tournament_permission, check_post_privileges
from common.auth import permissions, series_permissions, tournament_permissions
from common.data.commands import *
from common.data.models import *
from api.data import handle

@bind_request_body(CreateEditPostRequestData)
@require_permission(permissions.MANAGE_POSTS)
async def create_post(request: Request, body: CreateEditPostRequestData) -> JSONResponse:
    player_id = request.state.user.player_id
    command = CreatePostCommand(body.title, body.content, body.is_public, True, player_id)
    post_id = await handle(command)
    return JSONResponse({"id": post_id})

@bind_request_body(CreateEditPostRequestData)
@require_series_permission(series_permissions.MANAGE_SERIES_POSTS)
async def create_series_post(request: Request, body: CreateEditPostRequestData) -> JSONResponse:
    player_id = request.state.user.player_id
    series_id = request.path_params['series_id']
    command = CreatePostCommand(body.title, body.content, body.is_public, True, player_id, series_id=series_id)
    post_id = await handle(command)
    return JSONResponse({"id": post_id})

@bind_request_body(CreateEditPostRequestData)
@require_tournament_permission(tournament_permissions.MANAGE_TOURNAMENT_POSTS)
async def create_tournament_post(request: Request, body: CreateEditPostRequestData) -> JSONResponse:
    player_id = request.state.user.player_id
    tournament_id = request.path_params['tournament_id']
    command = CreatePostCommand(body.title, body.content, body.is_public, True, player_id, tournament_id=tournament_id)
    post_id = await handle(command)
    return JSONResponse({"id": post_id})

@bind_request_body(CreateEditPostRequestData)
@require_permission(permissions.MANAGE_POSTS)
async def edit_post(request: Request, body: CreateEditPostRequestData) -> JSONResponse:
    post_id = request.path_params['post_id']
    command = EditPostCommand(post_id, body.title, body.content, body.is_public, True)
    await handle(command)
    return JSONResponse({})

@bind_request_body(CreateEditPostRequestData)
@require_series_permission(series_permissions.MANAGE_SERIES_POSTS)
async def edit_series_post(request: Request, body: CreateEditPostRequestData) -> JSONResponse:
    post_id = request.path_params['post_id']
    series_id = request.path_params['series_id']
    command = EditPostCommand(post_id, body.title, body.content, body.is_public, True, series_id=series_id)
    await handle(command)
    return JSONResponse({})

@bind_request_body(CreateEditPostRequestData)
@require_tournament_permission(tournament_permissions.MANAGE_TOURNAMENT_POSTS)
async def edit_tournament_post(request: Request, body: CreateEditPostRequestData) -> JSONResponse:
    post_id = request.path_params['post_id']
    tournament_id = request.path_params['tournament_id']
    command = EditPostCommand(post_id, body.title, body.content, body.is_public, True, tournament_id=tournament_id)
    await handle(command)
    return JSONResponse({})

@bind_request_query(PostFilter)
@check_post_privileges
async def list_posts(request: Request, filter: PostFilter) -> JSONResponse:
    series_id = request.path_params.get('series_id', None)
    tournament_id = request.path_params.get('tournament_id', None)
    command = ListPostsCommand(filter, True, request.state.is_privileged, series_id, tournament_id)
    posts = await handle(command)
    return JSONResponse(posts)

@check_post_privileges
async def view_post(request: Request) -> JSONResponse:
    series_id = request.path_params.get('series_id', None)
    tournament_id = request.path_params.get('tournament_id', None)
    post_id = request.path_params['post_id']
    command = GetPostCommand(post_id, request.state.is_privileged, series_id, tournament_id)
    post = await handle(command)
    return JSONResponse(post)

routes: list[Route] = [
    Route('/api/posts/create', create_post, methods=['POST']),
    Route('/api/posts/{post_id:int}/edit', edit_post, methods=["POST"]),
    Route('/api/posts', list_posts),
    Route('/api/posts/{post_id:int}', view_post),
    Route('/api/tournaments/series/{series_id:int}/posts/create', create_series_post, methods=["POST"]),
    Route('/api/tournaments/series/{series_id:int}/posts/{post_id:int}/edit', edit_series_post, methods=["POST"]),
    Route('/api/tournaments/series/{series_id:int}/posts', list_posts),
    Route('/api/tournaments/series/{series_id:int}/posts/{post_id:int}', view_post),
    Route('/api/tournaments/{tournament_id:int}/posts/create', create_tournament_post, methods=["POST"]),
    Route('/api/tournaments/{tournament_id:int}/posts/{post_id:int}/edit', edit_tournament_post, methods=["POST"]),
    Route('/api/tournaments/{tournament_id:int}/posts', list_posts),
    Route('/api/tournaments/{tournament_id:int}/posts/{post_id:int}', view_post),
]