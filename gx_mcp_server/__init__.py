from fastmcp import FastMCP

# 1. Create the MCP server instance
mcp = FastMCP("gx-mcp-server")

# 2. Register tool modules
from .tools import datasets, expectations, validation  # noqa: E402

# 3. Expose the FastAPI app via SSE
app = mcp.sse_app()
