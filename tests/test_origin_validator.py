import pytest
from starlette.testclient import TestClient
from starlette.middleware import Middleware
from starlette.applications import Starlette
from starlette.routing import Route, Mount

from gx_mcp_server.server import create_server
from gx_mcp_server.origin_validator import OriginValidatorMiddleware
from gx_mcp_server.tools.health import health


def make_app(origins):
    mcp = create_server()
    mcp_app = mcp.http_app()
    middleware = [Middleware(OriginValidatorMiddleware, allowed_origins=origins)]
    app = Starlette(
        lifespan=mcp_app.lifespan,
        routes=[Route("/ping", health, methods=["GET"]), Mount("/", mcp_app)],
        middleware=middleware,
    )
    return app


@pytest.mark.parametrize("origin, status", [("https://ok.com", 200), ("https://bad.com", 400)])
def test_origin_validation(origin, status):
    app = make_app(["https://ok.com"])
    with TestClient(app) as client:
        resp = client.get("/ping", headers={"Origin": origin})
        assert resp.status_code == status
