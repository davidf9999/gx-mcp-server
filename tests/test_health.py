from gx_mcp_server.tools.health import ping


def test_ping():
    assert ping() == {"status": "ok"}
