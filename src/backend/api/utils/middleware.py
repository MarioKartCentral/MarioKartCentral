from starlette.middleware.base import BaseHTTPMiddleware
from api.utils.responses import ProblemResponse
from common.data.models import Problem
from starlette.background import BackgroundTasks
from api.data import handle
from common.data.commands import *
from api import appsettings

class ProblemHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            return await call_next(request)
        except Problem as problem:
            return ProblemResponse(problem)
        
class IPLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        async def log():
            if not appsettings.ENABLE_IP_LOGGING:
                return
            session_id = request.cookies.get("session", None)
            if not session_id:
                return
            user = await handle(GetUserIdFromSessionCommand(session_id))
            if not user:
                return
            ip_address = request.headers.get('CF-Connecting-IP', None) # use cloudflare headers if exists
            if not ip_address:
                ip_address = request.client.host if request.client else None
            await handle(LogUserIPCommand(user.id, ip_address))
        if request.method == "POST":
            tasks = BackgroundTasks()
            if response.background:
                tasks.add_task(response.background)
            tasks.add_task(log)
            response.background = tasks
        return response