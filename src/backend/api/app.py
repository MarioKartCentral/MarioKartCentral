from starlette.applications import Starlette
from api import settings
from api.data import init_db, init_s3
from api.endpoints import authservice, redisservice, roleservice, s3service, userservice, tournaments, tournament_registration

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
]

app = Starlette(debug=True, routes=routes, on_startup=[init_db, init_s3])
