from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route
import aiosqlite

# Hardcoded location for now, eventually should be managed as a docker or kubernetes volume 
DB_PATH = "mkc.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("CREATE TABLE IF NOT EXISTS users (name TEXT PRIMARY KEY)")
        await db.commit()

async def add_user(request: Request) -> Response:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO users VALUES (?)", [request.query_params["name"]])
        await db.commit()
    return Response(status_code=200)

async def list_users(request: Request) -> JSONResponse:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT name FROM users") as cursor:
            names = [row[0] for row in await cursor.fetchall()]
    return JSONResponse({'users': names})

async def homepage(request):
    return JSONResponse({'hello': 'world'})

routes = [
    Route('/', homepage),
    Route('/user/list', list_users),
    Route('/user', add_user, methods=["POST"])
]

app = Starlette(debug=True, routes=routes, on_startup=[init_db])