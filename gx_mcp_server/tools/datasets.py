# gx_mcp_server/tools/datasets.py
import io
import os
from pathlib import Path
from typing import TYPE_CHECKING, Literal

import pandas as pd

from gx_mcp_server.connectors import bigquery as bigquery_conn
from gx_mcp_server.connectors import snowflake as snowflake_conn

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
) -> schema.DatasetHandle | dict:
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
    try:
        if source.startswith("snowflake://"):
            df = snowflake_conn.load(source)
            handle = storage.DataStorage.add(df)
            logger.info(
                "Loaded dataset from Snowflake handle=%s (shape=%s)",
                handle,
                df.shape,
            )
            return schema.DatasetHandle(handle=handle)
        if source.startswith("bigquery://"):
            df = bigquery_conn.load(source)
            handle = storage.DataStorage.add(df)
            logger.info(
                "Loaded dataset from BigQuery handle=%s (shape=%s)",
                handle,
                df.shape,
            )
            return schema.DatasetHandle(handle=handle)
        # Reject large inline payloads
        if source_type == "inline" and len(source.encode("utf-8")) > LIMIT_BYTES:
            logger.warning(
                "Inline CSV too large: %d bytes (limit: %d MB)", len(source), limit_mb
            )
            return {"error": f"Inline CSV exceeds {limit_mb} MB limit"}

        if source_type == "file":
            path = Path(source)
            if path.is_file():
                if path.stat().st_size > LIMIT_BYTES:
                    logger.warning(
                        "Local CSV too large: %d bytes (limit: %d MB)",
                        path.stat().st_size,
                        limit_mb,
                    )
                    return {"error": f"Local CSV exceeds {limit_mb} MB limit"}
            df = pd.read_csv(path)
        elif source_type == "url":
            import requests  # type: ignore[import]
            from urllib.parse import urlparse

            parsed = urlparse(source)
            if parsed.scheme not in {"http", "https"}:
                return {"error": "Only http(s) URLs are allowed"}

            resp = requests.get(source, timeout=30, stream=True)
            resp.raise_for_status()
            # Enforce Content-Length if provided
            size = int(resp.headers.get("Content-Length", 0))
            if size > LIMIT_BYTES:
                logger.warning(
                    "Remote CSV too large: %d bytes (limit: %d MB)", size, limit_mb
                )
                return {"error": f"Remote CSV exceeds {limit_mb} MB limit"}
            if size == 0:
                # Stream download up to limit
                chunks = []
                total = 0
                for chunk in resp.iter_content(chunk_size=8192, decode_unicode=True):
                    if chunk:
                        total += len(chunk.encode("utf-8"))
                        if total > LIMIT_BYTES:
                            logger.warning(
                                "Remote CSV streamed exceeds %d MB limit", limit_mb
                            )
                            return {
                                "error": f"Remote CSV exceeds {limit_mb} MB limit"
                            }
                        chunks.append(chunk)
                txt = "".join(chunks)
            else:
                txt = resp.text
            df = pd.read_csv(io.StringIO(txt))
        elif source_type == "inline":
            df = pd.read_csv(io.StringIO(source))
        else:
            logger.error("Unknown source_type: %s", source_type)
            return {"error": f"Unknown source_type: {source_type}"}

        handle = storage.DataStorage.add(df)
        logger.info(
            "Loaded dataset handle=%s (shape=%s, columns=%s)", handle, df.shape, df.columns.tolist()
        )
        return schema.DatasetHandle(handle=handle)
    except Exception as e:
        logger.error("Failed to load dataset: %s", str(e))
        return {"error": f"Dataset loading failed: {str(e)}"}


def register(mcp_instance: "FastMCP") -> None:
    """Register dataset tools with the MCP instance."""
    mcp_instance.tool()(load_dataset)
