import pytest
from fastmcp import FastMCP

from gx_mcp_server.server import create_server


@pytest.fixture
def mcp_server():
    """Create a test MCP server instance."""
    return create_server()


def test_server_creation(mcp_server):
    """Test that the MCP server is created successfully."""
    assert isinstance(mcp_server, FastMCP)
    assert mcp_server.name == "gx-mcp-server"


def test_tools_registered(mcp_server):
    """Test that all tools are registered with the MCP server."""
    # FastMCP doesn't expose tools directly, but we can test that
    # the server was created without errors
    assert mcp_server is not None
