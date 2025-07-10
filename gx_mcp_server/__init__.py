# gx_mcp_server/__init__.py
from gx_mcp_server.logging import logger
from gx_mcp_server.server import create_server

__all__ = ["logger", "create_server"]
