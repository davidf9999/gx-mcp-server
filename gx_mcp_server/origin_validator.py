from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.requests import Request

class OriginValidatorMiddleware(BaseHTTPMiddleware):
    """Middleware to validate the Origin header against a list of allowed origins."""

    def __init__(self, app, allowed_origins: list[str]) -> None:
        super().__init__(app)
        self.allowed_origins = allowed_origins

    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("Origin")
        if origin and origin not in self.allowed_origins:
            return Response(status_code=400, content=b"Invalid Origin")
        return await call_next(request)
