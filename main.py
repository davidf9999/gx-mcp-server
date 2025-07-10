from starlette.responses import JSONResponse

from gx_mcp_server import logger, mcp
from gx_mcp_server.tools import register_tools

# Register tools with the MCP instance
register_tools(mcp)

# Add a simple health endpoint to the MCP instance
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    logger.debug("Health check invoked")
    return JSONResponse({"status": "ok"})

# Get the MCP app 
app = mcp.http_app()
