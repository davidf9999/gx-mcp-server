# gx_mcp_server/tools/datasets.py
import io
from pathlib import Path
from typing import Literal

import pandas as pd

from gx_mcp_server import logger
from gx_mcp_server.core import schema, storage


def _load_dataset(
    source: str,
    source_type: Literal["file", "url", "inline"] = "file",
) -> schema.DatasetHandle:
    """Load data (CSV string, URL, or local file) into memory and return a handle."""
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


def register(mcp_instance):
    mcp_instance.tool(name="load_dataset")(_load_dataset)
