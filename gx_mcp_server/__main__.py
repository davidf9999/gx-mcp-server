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
import os
import sys
from typing import TYPE_CHECKING, Any

from gx_mcp_server.server import create_server

if TYPE_CHECKING:  # pragma: no cover - only for type hints
    pass


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
    parser.add_argument(
        "--metrics-port",
        type=int,
        default=9090,
        help="Port to expose Prometheus metrics (default: 9090)",
    )
    parser.add_argument(
        "--trace",
        action="store_true",
        help="Enable OpenTelemetry tracing",
    )
    
    return parser.parse_args()


def setup_logging(level: str) -> None:
    """Configure logging for the application."""
    import logging

    class OTelFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:  # pragma: no cover - trivial
            record.otel = os.getenv("OTEL_RESOURCE_ATTRIBUTES", "")
            return True

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level),
        format="%(asctime)s [%(levelname)s] %(name)s %(otel)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stderr)],
    )
    logging.getLogger().addFilter(OTelFilter())
    
    # Reduce noise from some libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(logging.WARNING)


async def run_stdio() -> None:
    """Run MCP server in STDIO mode."""
    from gx_mcp_server import logger
    
    logger.info("Starting GX MCP Server in STDIO mode")
    mcp = create_server()
    
    # Run the server in STDIO mode
    await mcp.run_stdio_async()


def setup_tracing(app: Any) -> None:
    """Configure OpenTelemetry tracing."""
    from opentelemetry import trace
    from opentelemetry.instrumentation.asgi import OpenTelemetryMiddleware
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

    resource = Resource.create({"service.name": "gx-mcp-server"})
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(provider)
    app.add_middleware(OpenTelemetryMiddleware)


async def run_http(host: str, port: int, metrics_port: int, trace_enabled: bool) -> None:
    """Run MCP server in HTTP mode."""
    from gx_mcp_server import logger

    logger.info(f"Starting GX MCP Server in HTTP mode on {host}:{port}")
    mcp = create_server()
    app = mcp.http_app()

    if trace_enabled:
        setup_tracing(app)

    from prometheus_fastapi_instrumentator import Instrumentator
    from starlette.applications import Starlette
    instrumentator = Instrumentator().instrument(app)
    metrics_app = Starlette()
    instrumentator.expose(metrics_app, include_in_schema=False)

    import uvicorn

    config_main = uvicorn.Config(app, host=host, port=port, timeout_graceful_shutdown=0)
    server_main = uvicorn.Server(config_main)

    config_metrics = uvicorn.Config(metrics_app, host=host, port=metrics_port, log_level="info")
    server_metrics = uvicorn.Server(config_metrics)

    logger.info(f"Metrics available at http://{host}:{metrics_port}/metrics")

    await asyncio.gather(server_main.serve(), server_metrics.serve())


def show_inspector_instructions(host: str, port: int) -> None:
    """Run MCP server with inspector for development."""
    from gx_mcp_server import logger
    
    logger.info(f"Starting GX MCP Server with Inspector on {host}:{port}")
    logger.info("The MCP Inspector should be run as a separate tool.")
    logger.info("To use the MCP Inspector with this server:")
    logger.info("1. Start this server in HTTP mode: python -m gx_mcp_server --http")
    logger.info("2. In another terminal, run: npx @modelcontextprotocol/inspector")
    logger.info("3. Connect the inspector to http://localhost:8000")
    
    # For now, run the server in HTTP mode as a fallback
    mcp = create_server()
    asyncio.run(mcp.run_http_async(host=host, port=port))


def main() -> None:
    """Main entry point."""
    args = parse_args()
    if args.trace:
        os.environ.setdefault("OTEL_RESOURCE_ATTRIBUTES", "service.name=gx-mcp-server")
    setup_logging(args.log_level)
    
    try:
        if args.inspect:
            # Inspector mode (synchronous)
            show_inspector_instructions(args.host, args.port)
        elif args.http:
            # HTTP mode (async)
            asyncio.run(run_http(args.host, args.port, args.metrics_port, args.trace))
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