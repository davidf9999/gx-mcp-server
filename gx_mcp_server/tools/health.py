"""Simple health check tool."""
from typing import TYPE_CHECKING

from gx_mcp_server.logging import logger

if TYPE_CHECKING:
    from fastmcp import FastMCP


def ping() -> dict:
    """Return basic health status."""
    logger.debug("Health check ping")
    return {"status": "ok"}


def register(mcp_instance: "FastMCP") -> None:
    """Register health tools."""
    mcp_instance.tool()(ping)
