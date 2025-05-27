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
import ipaddress
from typing import Any
from starlette.requests import Request
from opentelemetry import trace
from opentelemetry.trace.status import Status, StatusCode

async def handle_error(request: Request, exception: Exception):
    logging.getLogger().error("Unhandled Exception", exc_info=exception)
    return ProblemResponse(Problem("Unexpected Error"))

async def handle_problem(request: Request, problem: Problem):
    if problem.status >= 500:
        logging.getLogger().error(f"Problem: {problem}", exc_info=problem)
    span = trace.get_current_span()
    if span and span.is_recording():
        span.record_exception(problem)
        span.set_status(Status(StatusCode.ERROR, str(problem)))
    return ProblemResponse(problem)

exception_handlers: dict[Any, Any] = {
    Problem: handle_problem,
    500: handle_error
}


class ProblemExceptionMiddleware:
    """
    Catches any Problems that might have been raised during the middleware
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        try:
            await self.app(scope, receive, send)
        except Problem as problem:
            logging.getLogger().error(f"Problem: {problem}", exc_info=problem)
            span = trace.get_current_span()
            if span.is_recording():
                span.record_exception(problem)
                span.set_status(Status(StatusCode.ERROR, str(problem)))
            response = ProblemResponse(problem)
            await response(scope, receive, send)

        
class IPLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        time = datetime.now(timezone.utc)
        path = request.url.path
        
        should_log = appsettings.ENABLE_IP_LOGGING and (
            request.method == "POST" or
            path == "/api/user/me" or 
            path == "/api/user/me/player"
        ) 

        ip_address = request.headers.get('CF-Connecting-IP')
        if ip_address is None and appsettings.ENV == "Development":
            if request.client is not None:
                ip_address = request.client.host

        if ip_address is not None:
            ip_obj = ipaddress.ip_address(ip_address)
            if isinstance(ip_obj, ipaddress.IPv6Address):
                full_addr = ip_obj.exploded
                parts = full_addr.split(":")
                ip_address = ":".join(parts[:4]) + "::"

        request.state.ip_address = ip_address
        
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
        ip_address = scope["state"]["ip_address"]
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
                r"/api/tournaments/\d+/create": [Rule(minute=3, hour=10)],
                r"^/api/tournaments/\d+/edit": [Rule(minute=3, hour=10)],
            },
            on_blocked=self.on_blocked
        )
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        await self.rate_limit(scope, receive, send)