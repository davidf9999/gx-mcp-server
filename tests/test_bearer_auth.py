import pytest
from starlette.testclient import TestClient

from fastmcp.server.auth.providers.bearer import BearerAuthProvider, RSAKeyPair
from gx_mcp_server.server import create_server


def make_app():
    keypair = RSAKeyPair.generate()
    provider = BearerAuthProvider(public_key=keypair.public_key, audience="gx-mcp")
    server = create_server(provider)
    return server.http_app(), keypair


@pytest.mark.asyncio
async def test_bearer_required():
    app, keypair = make_app()
    with TestClient(app) as client:
        resp = client.get("/mcp/")
        assert resp.status_code == 401
        token = keypair.create_token(audience="gx-mcp")
        resp_ok = client.get("/mcp/", headers={"Authorization": f"Bearer {token}"})
        assert resp_ok.status_code != 401

