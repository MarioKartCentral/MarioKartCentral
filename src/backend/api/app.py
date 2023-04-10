from starlette.applications import Starlette
from starlette.middleware import Middleware
from api import settings
from api.data import init_db, init_s3, close_s3
from api.endpoints import authservice, redisservice, roleservice, s3service, userservice, tournaments, tournament_registration, player_registry, user_settings
from api.utils.middleware import ProblemHandlingMiddleware
from api.utils.schema_gen import schema_route

if settings.DEBUG:
    import debugpy
    debugpy.listen(("0.0.0.0", 5678))
    debugpy.wait_for_client()  # blocks execution until client is attached

routes = [
    *authservice.routes,
    *redisservice.routes,
    *roleservice.routes,
    *s3service.routes,
    *userservice.routes,
    *tournaments.routes,
    *tournament_registration.routes,
    *player_registry.routes,
    *user_settings.routes,
    schema_route
]

middleware = [
    Middleware(ProblemHandlingMiddleware)
]

app = Starlette(debug=True, routes=routes, on_startup=[init_db, init_s3], on_shutdown=[close_s3], middleware=middleware)
