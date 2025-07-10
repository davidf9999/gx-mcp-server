# gx_mcp_server/__init__.py
import logging

try:
    from fastmcp import FastMCP  # type: ignore
except Exception:  # pragma: no cover - fastmcp optional for tests
    from fastapi import APIRouter, FastAPI

    class FastMCP:  # minimal fallback used in CI where fastmcp is unavailable
        """Lightweight stub mimicking the FastMCP interface."""

        def __init__(self, name: str) -> None:  # noqa: D401 - trivial
            self.router = APIRouter()

        def tool(self):  # noqa: D401 - simple decorator
            def decorator(func):
                return func

            return decorator

        def http_app(self) -> FastAPI:
            app = FastAPI(title="GX MCP Server")
            app.include_router(self.router)
            return app


# Configure logger
logger = logging.getLogger("gx_mcp_server")

# Avoid adding multiple handlers when the module is imported repeatedly
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    )
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# 1. Create the MCP server instance
mcp: FastMCP = FastMCP("gx-mcp-server")
# …
app = mcp.http_app()
