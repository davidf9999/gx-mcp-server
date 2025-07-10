from fastapi import FastAPI

from gx_mcp_server import logger, mcp
from gx_mcp_server.tools import register_tools

# Register tools with the MCP instance
register_tools(mcp)

# Create FastAPI app - this gives us automatic /docs
app = FastAPI(
    title="GX MCP Server",
    description="Great Expectations MCP Server - provides data validation via MCP tools",
    version="1.0.0"
)

# Add health endpoint to FastAPI
@app.get("/health", tags=["Health"])
def health():
    """Health check endpoint"""
    logger.debug("Health check invoked")
    return {"status": "ok"}

# Add info endpoint about MCP tools
@app.get("/mcp/info", tags=["MCP Tools"])
def mcp_info():
    """Information about available MCP tools"""
    return {
        "tools": [
            {"name": "load_dataset", "description": "Load CSV data from file, URL, or inline string"},
            {"name": "create_suite", "description": "Create Great Expectations suite with optional profiling"},
            {"name": "add_expectation", "description": "Add individual expectations to existing suites"},
            {"name": "run_checkpoint", "description": "Execute validation checkpoints against datasets"},
            {"name": "get_validation_result", "description": "Retrieve detailed validation results"}
        ],
        "protocol": "MCP (Model Context Protocol)",
        "client_url": "http://localhost:8000/mcp"
    }

# Mount MCP app at /mcp
mcp_app = mcp.http_app()
app.mount("/mcp", mcp_app)
