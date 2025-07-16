import pytest
import httpx
from starlette.responses import JSONResponse
from starlette.requests import Request

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.extension import Limiter
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.middleware import Middleware

from gx_mcp_server.server import create_server


def make_app(limit: int):
    mcp = create_server()

    @mcp.custom_route("/ping", methods=["GET"])
    async def ping(request: Request):  # pragma: no cover - simple test route
        return JSONResponse({"status": "ok"})

    limiter = Limiter(key_func=get_remote_address, default_limits=[f"{limit}/minute"])
    middleware = [Middleware(SlowAPIMiddleware)]
    app = mcp.http_app(middleware=middleware)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    return app


@pytest.mark.asyncio
async def test_rate_limit_exceeded():
    app = make_app(2)
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        for _ in range(2):
            resp = await client.get("/ping")
            assert resp.status_code == 200
        resp = await client.get("/ping")
        assert resp.status_code == 429
