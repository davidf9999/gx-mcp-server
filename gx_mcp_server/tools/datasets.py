# gx_mcp_server/tools/datasets.py
import io
from pathlib import Path
from typing import Literal

import pandas as pd
from gx_mcp_server import mcp
from gx_mcp_server.core import storage, schema


@mcp.tool()
def load_dataset(
    source: str,
    source_type: Literal["file", "url", "inline"] = "file",
) -> schema.DatasetHandle:
    """Load data (CSV string, URL, or local file) into memory and return a handle."""
    if source_type == "file":
        df = pd.read_csv(Path(source))
    elif source_type == "url":
        import requests

        txt = requests.get(source, timeout=30).text
        df = pd.read_csv(io.StringIO(txt))
    else:
        df = pd.read_csv(io.StringIO(source))
    handle = storage.DataStorage.add(df)
    return schema.DatasetHandle(handle=handle)


# Expose direct function for tests
load_dataset = load_dataset.fn