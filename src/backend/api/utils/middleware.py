import sys
import traceback
from starlette.middleware.base import BaseHTTPMiddleware
from api.utils.responses import ProblemResponse
from common.data.models import Problem

class ProblemHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            return await call_next(request)
        except Problem as problem:
            print(f"Problem: {problem}", file=sys.stderr)
            if problem.status > 500:
                traceback.print_exc()
            return ProblemResponse(problem)