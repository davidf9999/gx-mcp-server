from fastapi import FastAPI

from gx_mcp_server import logger, mcp
from gx_mcp_server.tools import register_tools

# Create the main FastAPI app
app = FastAPI(title="GX MCP Server")


# Add a simple health endpoint to the main FastAPI app
@app.get("/health")
def health():
    logger.info("Health check invoked")
    return {"status": "ok"}


# Register tools with the MCP instance
register_tools(mcp)

# Include the MCP router
app.mount("/mcp", mcp.http_app())
