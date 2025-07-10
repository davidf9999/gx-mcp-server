# gx_mcp_server/__init__.py
import logging

from fastmcp import FastMCP
# from starlette.requests import Request
# from starlette.responses import JSONResponse, Response

# Configure logger
logger = logging.getLogger("gx_mcp_server")

# Avoid adding multiple handlers when the module is imported repeatedly
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    )
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

# Create the MCP server instance
mcp: FastMCP = FastMCP("gx-mcp-server")



