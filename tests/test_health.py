import httpx
import pytest

from starlette.applications import Starlette
from starlette.routing import Mount, Route
from gx_mcp_server.server import create_server
from gx_mcp_server.tools.health import ping, health


def test_ping():
    assert ping() == {"status": "ok"}


@pytest.mark.asyncio
async def test_health_route():
    mcp = create_server()
    mcp_app = mcp.http_app()
    app = Starlette(
        lifespan=mcp_app.lifespan,
        routes=[
            Route("/mcp/health", health, methods=["GET"]),
            Mount("/", mcp_app),
        ],
    )

    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/mcp/health")
    assert resp.status_code == 200
