"""
GX MCP Server implementation.

This module creates and configures the FastMCP server instance with all
Great Expectations tools registered.
"""

from fastmcp import FastMCP

from gx_mcp_server.logging import logger
from fastmcp.server.auth.auth import OAuthProvider


def create_server(auth: OAuthProvider | None = None) -> FastMCP:
    """Create and configure the GX MCP server with all tools registered.

    Args:
        auth: Optional OAuth provider for Bearer token authentication.

    Returns:
        FastMCP: Configured MCP server instance
    """
    logger.debug("Creating GX MCP server instance")
    
    # Create the MCP server
    mcp: FastMCP = FastMCP("gx-mcp-server", auth=auth)
    
    # Register all tools
    from gx_mcp_server.tools import register_tools
    register_tools(mcp)
    
    logger.debug("GX MCP server created and tools registered")
    return mcp