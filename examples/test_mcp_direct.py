#!/usr/bin/env python3
"""Test script to run MCP server directly"""

from gx_mcp_server import mcp
from gx_mcp_server.tools import register_tools

# Register tools
register_tools(mcp)

if __name__ == "__main__":
    # Run the MCP server directly
    mcp.run()