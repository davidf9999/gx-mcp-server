from fastapi import FastAPI

from . import app as mcp_app
from . import logger

app: FastAPI = mcp_app


@app.get("/health")
def health():
    logger.info("Health check")
    return {"status": "ok"}
