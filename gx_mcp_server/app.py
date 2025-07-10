from fastapi import FastAPI

from gx_mcp_server import logger

from . import app as mcp_app

# Create a proper FastAPI instance
app = FastAPI(title="GX MCP Server")

# Include the MCP app's router so its endpoints show up in the docs
app.include_router(mcp_app.router, prefix="/mcp")


# Add a simple health endpoint
@app.get("/health")
def health():
    logger.info("Health check invoked")
    return {"status": "ok"}
