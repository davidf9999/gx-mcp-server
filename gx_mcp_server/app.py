from fastapi import FastAPI

from gx_mcp_server import logger

from . import app as mcp_app

# Create a proper FastAPI instance
app = FastAPI(title="GX MCP Server")

# Mount the MCP HTTP app at the root
app.mount("/", mcp_app)


# Add a simple health endpoint
@app.get("/health")
def health():
    logger.info("Health check invoked")
    return {"status": "ok"}
