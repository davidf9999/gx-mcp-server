#!/usr/bin/env python3
"""Test script to run MCP server directly"""

import asyncio
from gx_mcp_server.server import create_server

async def main() -> None:
    """Run the MCP server in STDIO mode."""
    mcp = create_server()
    await mcp.run_stdio_async()

if __name__ == "__main__":
    # Run the MCP server directly in STDIO mode
    asyncio.run(main())