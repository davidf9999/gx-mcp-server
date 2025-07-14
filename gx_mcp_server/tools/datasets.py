# gx_mcp_server/tools/datasets.py
import io
import os
from pathlib import Path
from typing import TYPE_CHECKING, Literal

import pandas as pd

from gx_mcp_server.logging import logger
from gx_mcp_server.core import schema, storage

if TYPE_CHECKING:
    from fastmcp import FastMCP


def get_csv_size_limit_bytes() -> int:
    """
    Get CSV size limit in bytes from the environment, defaulting to 50MB.
    Limits to range [1, 1024] MB.
    """
    DEFAULT_MB = 50
    min_mb, max_mb = 1, 1024
    value = os.getenv("MCP_CSV_SIZE_LIMIT_MB")
    try:
        mb = int(value) if value else DEFAULT_MB
        if mb < min_mb or mb > max_mb:
            mb = DEFAULT_MB
    except Exception:
        mb = DEFAULT_MB
    return mb * 1024 * 1024


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
    LIMIT_BYTES = get_csv_size_limit_bytes()
    limit_mb = LIMIT_BYTES // (1024 * 1024)

    # Reject large inline payloads
    if source_type == "inline" and len(source.encode("utf-8")) > LIMIT_BYTES:
        logger.warning(
            "Inline CSV too large: %d bytes (limit: %d MB)", len(source), limit_mb
        )
        raise ValueError(f"Inline CSV exceeds {limit_mb} MB limit")

    if source_type == "file":
        df = pd.read_csv(Path(source))
    elif source_type == "url":
        import requests  # type: ignore[import]

        resp = requests.get(source, timeout=30, stream=True)
        resp.raise_for_status()
        # Enforce Content-Length if provided
        size = int(resp.headers.get("Content-Length", 0))
        if size > LIMIT_BYTES:
            logger.warning(
                "Remote CSV too large: %d bytes (limit: %d MB)", size, limit_mb
            )
            raise ValueError(f"Remote CSV exceeds {limit_mb} MB limit")
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
