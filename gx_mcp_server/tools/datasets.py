# gx_mcp_server/tools/datasets.py
import io
from pathlib import Path
from typing import TYPE_CHECKING, Literal

import pandas as pd

from gx_mcp_server import logger
from gx_mcp_server.core import schema, storage

if TYPE_CHECKING:
    from fastmcp import FastMCP


def load_dataset(
    source: str,
    source_type: Literal["file", "url", "inline"] = "file",
) -> schema.DatasetHandle:
    """Load data (CSV string, URL, or local file) into memory and return a handle.
    
    Args:
        source: Path to file, URL, or inline CSV string
        source_type: Type of source - "file", "url", or "inline"
        
    Returns:
        DatasetHandle: Handle to the loaded dataset for use in other tools
        
    Examples:
        - File: load_dataset("/path/to/data.csv", "file")
        - URL: load_dataset("https://example.com/data.csv", "url") 
        - Inline: load_dataset("x,y\\n1,2\\n3,4", "inline")
    """
    logger.info("Called load_dataset(source_type=%s)", source_type)
    
    # Reject large inline payloads
    if source_type == "inline" and len(source.encode("utf-8")) > 50 * 1024**2:
        logger.warning("Inline CSV too large: %d bytes", len(source))
        raise ValueError("Inline CSV exceeds 50 MB limit")

    if source_type == "file":
        df = pd.read_csv(Path(source))
    elif source_type == "url":
        import requests  # type: ignore[import]

        resp = requests.get(source, timeout=30, stream=True)
        resp.raise_for_status()
        # Enforce Content-Length if provided
        size = int(resp.headers.get("Content-Length", 0))
        if size > 50 * 1024**2:
            logger.warning("Remote CSV too large: %d bytes", size)
            raise ValueError("Remote CSV exceeds 50 MB limit")
        txt = resp.text
        df = pd.read_csv(io.StringIO(txt))
    else:
        df = pd.read_csv(io.StringIO(source))
        
    handle = storage.DataStorage.add(df)
    logger.info(
        "Loaded dataset handle=%s (%d rows, %d cols)", handle, len(df), len(df.columns)
    )
    return schema.DatasetHandle(handle=handle)


def register(mcp_instance: "FastMCP") -> None:
    """Register dataset tools with the MCP instance."""
    mcp_instance.tool()(load_dataset)
