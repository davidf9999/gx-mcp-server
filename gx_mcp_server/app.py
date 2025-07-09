"""
Starlette/FastAPI app entrypoint for uvicorn and pytest.
Importable as `gx_mcp_server.app:app`.
"""
# import the SSE app from package root

from . import app  # re-export from package root
