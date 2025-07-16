import base64
from starlette.testclient import TestClient
from starlette.middleware import Middleware

from gx_mcp_server.server import create_server
from gx_mcp_server.basic_auth import BasicAuthMiddleware


def create_app(use_auth: bool):
    server = create_server()
    middleware = []
    if use_auth:
        middleware.append(Middleware(BasicAuthMiddleware, username="user", password="pass"))
    return server.http_app(middleware=middleware)


def test_no_auth_allowed():
    app = create_app(False)
    with TestClient(app) as client:
        resp = client.get("/mcp/")
        assert resp.status_code != 401


def test_basic_auth_required():
    app = create_app(True)
    with TestClient(app) as client:
        resp = client.get("/mcp/")
        assert resp.status_code == 401
        token = base64.b64encode(b"user:pass").decode()
        resp_ok = client.get("/mcp/", headers={"Authorization": f"Basic {token}"})
        assert resp_ok.status_code != 401

