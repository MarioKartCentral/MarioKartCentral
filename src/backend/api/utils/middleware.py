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
        time = datetime.now(timezone.utc)
        path = request.url.path
        
        should_log = appsettings.ENABLE_IP_LOGGING and (
            request.method == "POST" or
            path == "/api/user/me" or 
            path == "/api/user/me/player"
        ) 
        
        response = await call_next(request)
        
        async def log_activity():
            if not appsettings.ENABLE_IP_LOGGING:
                return
            
            # Try to get user from request.state first (might be set by auth middleware)
            user = getattr(request.state, 'user', None)
            if user is None:
                # If not available, check session and get user info
                session_id = request.cookies.get("session", None)
                if not session_id:
                    return
                    
                user = await handle(GetUserIdFromSessionCommand(session_id))
                if not user:
                    return
                
            ip_address = request.headers.get('CF-Connecting-IP', None) # use cloudflare headers if exists
            if not ip_address:
                ip_address = request.client.host if request.client else None
            
            # Get referer header if available
            referer = request.headers.get('Referer', None)
                
            # Log to activity queue instead of directly processing
            await handle(EnqueueUserActivityCommand(
                user_id=user.id,
                ip_address=ip_address,
                path=path,
                timestamp=time,
                referer=referer
            ))
        
        # Only log for POST requests and specific endpoints
        if should_log:
            tasks = BackgroundTasks()
            if response.background:
                tasks.add_task(response.background)
                
            tasks.add_task(log_activity)
            response.background = tasks
            
        return response

class RateLimitByIPMiddleware:
    async def auth_function(self, scope: Scope):
        ip_address = scope.get('CF-Connecting-IP', None)
        if not ip_address:
            ip_address = scope['client'][0]
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