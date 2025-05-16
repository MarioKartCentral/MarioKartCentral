
from starlette.applications import Starlette
from starlette.middleware import Middleware
from api import appsettings
from api.data import on_startup, on_shutdown
from api.endpoints import (authservice, roleservice, userservice, tournaments, 
                           tournament_registration, tournament_placements, player_registry, player_bans, 
                           team_registry, user_settings, notifications, moderation, mkcv1importer, posts,
                           admin)
from api.utils.middleware import IPLoggingMiddleware, RateLimitByIPMiddleware, exception_handlers
from api.utils.schema_gen import schema_route
from common.logging_setup import setup_logging
from starlette.routing import Route
from starlette_prometheus import metrics, PrometheusMiddleware


setup_logging()

if appsettings.DEBUG:
    import debugpy
    debugpy.listen(("0.0.0.0", 5678))
    debugpy.wait_for_client()  # blocks execution until client is attached

routes = [
    *admin.routes,
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
    schema_route,
    Route("/metrics", metrics),
]


middleware = [
    Middleware(IPLoggingMiddleware),
    Middleware(RateLimitByIPMiddleware),
    Middleware(PrometheusMiddleware),
]

app = Starlette(routes=routes, on_startup=[on_startup], on_shutdown=[on_shutdown], middleware=middleware, exception_handlers=exception_handlers)
