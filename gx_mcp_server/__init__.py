# gx_mcp_server/__init__.py
from fastmcp import FastMCP

# 1. Create the MCP server instance
mcp = FastMCP("gx-mcp-server")

# 2. Register tool modules
from .tools import datasets, expectations, validation  # noqa: E402

# 3. Expose the FastAPI app via http_app (modern API)
# `sse_app()` is deprecated; `http_app` is the new entrypoint
app = mcp.http_app()
