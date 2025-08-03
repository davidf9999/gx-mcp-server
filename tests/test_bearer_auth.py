import time

import pytest
from starlette.testclient import TestClient
from authlib.jose import jwt

from gx_mcp_server.bearer_auth import BearerAuthProvider
from gx_mcp_server.server import create_server
from fastmcp.server.auth.providers.bearer import RSAKeyPair


@pytest.fixture
def keypair():
    return RSAKeyPair.generate()


def make_app(provider):
    server = create_server(provider)
    return server.http_app()


@pytest.mark.asyncio
async def test_bearer_required(keypair):
    provider = BearerAuthProvider(public_key=keypair.public_key, audience="gx-mcp")
    app = make_app(provider)
    with TestClient(app) as client:
        resp = client.get("/mcp/")
        assert resp.status_code == 401
        token = keypair.create_token(audience="gx-mcp")
        resp_ok = client.get("/mcp/", headers={"Authorization": f"Bearer {token}"})
        assert resp_ok.status_code != 401


@pytest.mark.asyncio
async def test_invalid_issuer(keypair):
    provider = BearerAuthProvider(
        public_key=keypair.public_key, issuer="my-issuer", audience="gx-mcp"
    )
    app = make_app(provider)
    with TestClient(app) as client:
        header = {"alg": "RS256"}
        payload = {"iss": "wrong-issuer", "aud": "gx-mcp", "exp": int(time.time()) + 3600}
        private_key_bytes = keypair.private_key.get_secret_value().encode("utf-8")
        token = jwt.encode(header, payload, private_key_bytes)
        resp = client.get("/mcp/", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 401


@pytest.mark.asyncio
async def test_invalid_audience(keypair):
    provider = BearerAuthProvider(public_key=keypair.public_key, audience="gx-mcp")
    app = make_app(provider)
    with TestClient(app) as client:
        token = keypair.create_token(audience="wrong-audience")
        resp = client.get("/mcp/", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 401


@pytest.mark.asyncio
async def test_expired_token(keypair):
    provider = BearerAuthProvider(public_key=keypair.public_key, audience="gx-mcp")
    app = make_app(provider)
    with TestClient(app) as client:
        header = {"alg": "RS256"}
        payload = {"aud": "gx-mcp", "exp": int(time.time()) - 1}
        private_key_bytes = keypair.private_key.get_secret_value().encode("utf-8")
        token = jwt.encode(header, payload, private_key_bytes)
        resp = client.get("/mcp/", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 401

