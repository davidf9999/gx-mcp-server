# gx_mcp_server/__init__.py
import logging

from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

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

# Create the MCP server instance
mcp: FastMCP = FastMCP("gx-mcp-server")


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> Response:
    logger.info("Health check invoked")
    return JSONResponse({"status": "ok"})
