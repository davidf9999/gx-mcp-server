from fastmcp import FastMCP

# Import tools to register them with the MCP instance
from . import datasets, expectations, validation


def register_tools(mcp_instance: FastMCP) -> None:
    from gx_mcp_server.logging import logger
    logger.debug("Registering tools with MCP instance")
    datasets.register(mcp_instance)
    expectations.register(mcp_instance)
    validation.register(mcp_instance)
