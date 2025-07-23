from __future__ import annotations

import base64
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.requests import Request

class BasicAuthMiddleware(BaseHTTPMiddleware):
    """Simple HTTP Basic authentication middleware."""

    def __init__(self, app, username: str, password: str) -> None:
        super().__init__(app)
        self._expected = f"{username}:{password}"

    async def dispatch(self, request: Request, call_next):
        # Allow OPTIONS requests to pass through without authentication
        if request.method == "OPTIONS":
            return await call_next(request)

        auth = request.headers.get("Authorization")
        if not auth or not auth.lower().startswith("basic "):
            return Response(status_code=401, headers={"WWW-Authenticate": "Basic"})
        try:
            decoded = base64.b64decode(auth.split(" ", 1)[1]).decode()
        except Exception:
            return Response(status_code=401, headers={"WWW-Authenticate": "Basic"})
        if decoded != self._expected:
            return Response(status_code=401, headers={"WWW-Authenticate": "Basic"})
        return await call_next(request)
