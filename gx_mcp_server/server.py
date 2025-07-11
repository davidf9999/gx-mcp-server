"""
GX MCP Server implementation.

This module creates and configures the FastMCP server instance with all
Great Expectations tools registered.
"""

from fastmcp import FastMCP

from gx_mcp_server.logging import logger


def create_server() -> FastMCP:
    """
    Create and configure the GX MCP server with all tools registered.
    
    Returns:
        FastMCP: Configured MCP server instance
    """
    logger.debug("Creating GX MCP server instance")
    
    # Create the MCP server
    mcp: FastMCP = FastMCP("gx-mcp-server")
    
    # Register all tools
    from gx_mcp_server.tools import register_tools
    register_tools(mcp)
    
    logger.debug("GX MCP server created and tools registered")
    return mcp