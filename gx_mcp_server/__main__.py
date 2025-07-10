#!/usr/bin/env python3
"""
CLI entry point for GX MCP Server.

Supports multiple transport modes:
- STDIO: For AI clients like Claude Desktop (default)
- HTTP: For web-based clients
- Inspector: Development mode with web UI for testing
"""

import argparse
import asyncio
import sys

from gx_mcp_server.server import create_server


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Great Expectations MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m gx_mcp_server                    # STDIO mode (default)
  python -m gx_mcp_server --http             # HTTP mode on localhost:8000
  python -m gx_mcp_server --http --port 3000 # HTTP mode on custom port
  python -m gx_mcp_server --inspect          # Development mode with web UI
        """,
    )
    
    transport_group = parser.add_mutually_exclusive_group()
    transport_group.add_argument(
        "--http",
        action="store_true",
        help="Run HTTP server (default: STDIO mode)",
    )
    transport_group.add_argument(
        "--inspect",
        action="store_true", 
        help="Run with MCP Inspector for development/testing",
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for HTTP server (default: 8000)",
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Host for HTTP server (default: localhost)",
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)",
    )
    
    return parser.parse_args()


def setup_logging(level: str) -> None:
    """Configure logging for the application."""
    import logging
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stderr)],
    )
    
    # Reduce noise from some libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(logging.WARNING)


async def run_stdio() -> None:
    """Run MCP server in STDIO mode."""
    from gx_mcp_server import logger
    
    logger.info("Starting GX MCP Server in STDIO mode")
    mcp = create_server()
    
    # Run the server in STDIO mode
    await mcp.run_stdio()


async def run_http(host: str, port: int) -> None:
    """Run MCP server in HTTP mode."""
    from gx_mcp_server import logger
    
    logger.info(f"Starting GX MCP Server in HTTP mode on {host}:{port}")
    mcp = create_server()
    
    # Run the server in HTTP mode
    await mcp.run_http(host=host, port=port)


def run_inspector(host: str, port: int) -> None:
    """Run MCP server with inspector for development."""
    from gx_mcp_server import logger
    
    logger.info(f"Starting GX MCP Server with Inspector on {host}:{port}")
    mcp = create_server()
    
    # Run with MCP Inspector (synchronous)
    mcp.run_inspector(host=host, port=port)


def main() -> None:
    """Main entry point."""
    args = parse_args()
    setup_logging(args.log_level)
    
    try:
        if args.inspect:
            # Inspector mode (synchronous)
            run_inspector(args.host, args.port)
        elif args.http:
            # HTTP mode (async)
            asyncio.run(run_http(args.host, args.port))
        else:
            # STDIO mode (async, default)
            asyncio.run(run_stdio())
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()