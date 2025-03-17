from starlette.applications import Starlette
from starlette.middleware import Middleware
from api import appsettings
from api.data import on_startup, on_shutdown
from api.endpoints import (authservice, roleservice, userservice, tournaments, 
                           tournament_registration, tournament_placements, player_registry, player_bans, 
                           team_registry, user_settings, notifications, moderation, mkcv1importer, posts)
from api.utils.middleware import ProblemHandlingMiddleware
from api.utils.schema_gen import schema_route

if appsettings.DEBUG:
    import debugpy
    debugpy.listen(("0.0.0.0", 5678))
    debugpy.wait_for_client()  # blocks execution until client is attached

routes = [
    *authservice.routes,
    *mkcv1importer.routes,
    *moderation.routes,
    *roleservice.routes,
    *userservice.routes,
    *tournaments.routes,
    *tournament_registration.routes,
    *tournament_placements.routes,
    *player_registry.routes,
    *player_bans.routes,
    *team_registry.routes,
    *user_settings.routes,
    *notifications.routes,
    *posts.routes,
    schema_route
]

middleware = [
    Middleware(ProblemHandlingMiddleware)
]

app = Starlette(debug=True, routes=routes, on_startup=[on_startup], on_shutdown=[on_shutdown], middleware=middleware)
