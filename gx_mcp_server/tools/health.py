"""Simple health check tool."""

from typing import TYPE_CHECKING

from starlette.requests import Request
from starlette.responses import Response

from gx_mcp_server.logging import logger

if TYPE_CHECKING:
    from fastmcp import FastMCP


def ping() -> dict:
    """Return basic health status."""
    logger.debug("Health check ping")
    return {"status": "ok"}


async def health(_: Request) -> Response:
    """HTTP health endpoint."""
    logger.debug("HTTP health check")
    return Response(status_code=200, content="OK")


def register(mcp_instance: "FastMCP") -> None:
    """Register health tools."""
    mcp_instance.tool()(ping)
