import sys
import traceback
from starlette.middleware.base import BaseHTTPMiddleware
from api.utils.responses import ProblemResponse
from common.data.models import Problem
from starlette.background import BackgroundTasks
from api.data import handle
from common.data.commands import *
from api import appsettings
from ratelimit.types import ASGIApp, Scope, Receive, Send
from ratelimit import RateLimitMiddleware, Rule
from ratelimit.backends.simple import MemoryBackend

class ProblemHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            return await call_next(request)
        except Problem as problem:
            print(f"Problem: {problem}", file=sys.stderr)
            if problem.status > 500:
                traceback.print_exc()
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

class RateLimitByIPMiddleware:
    async def auth_function(self, scope: Scope):
        ip_address = scope.get('CF-Connecting-IP', None)
        if not ip_address:
            ip_address = scope['client'][0]
        print(ip_address)
        return ip_address, 'default'
    
    def on_blocked(self, retry_after: int):
        async def inside_on_blocked(scope: Scope, receive: Receive, send: Send):
            raise Problem(f"You have been rate limited, try again in {retry_after} seconds", status=429)
        return inside_on_blocked
    
    def __init__(self, app: ASGIApp):
        self.app = app
        self.rate_limit = RateLimitMiddleware(
            self.app,
            self.auth_function,
            MemoryBackend(),
            config={
                r"/api/user/signup": [Rule(minute=3, hour=10)],
                r"/api/user/send_confirmation_email": [Rule(minute=3, hour=10)],
                r"/api/user/forgot_password": [Rule(minute=3, hour=10)],
                r"/api/user/transfer_account": [Rule(minute=3, hour=10)],
                r"/api/user/change_email": [Rule(minute=3, hour=10)],
                r"/api/user/refresh_discord": [Rule(minute=3, hour=10)],
                r"/api/user/discord_callback": [Rule(minute=3, hour=10)],
                r"/api/user/sync_discord_avatar": [Rule(minute=3, hour=10)],
                r"/api/registry/teams/edit": [Rule(minute=3, hour=10)],
                r"/api/tournaments/.*/create": [Rule(minute=3, hour=10)],
                r"/api/tournaments/.*/edit": [Rule(minute=3, hour=10)],
            },
            on_blocked=self.on_blocked
        )
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        await self.rate_limit(scope, receive, send)
        await self.app(scope, receive, send)