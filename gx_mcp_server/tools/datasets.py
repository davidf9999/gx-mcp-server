import io
from pathlib import Path
from typing import Literal

import pandas as pd
from fastmcp import tool

from gx_mcp_server import mcp
from gx_mcp_server.core import storage, schema

@tool(mcp)
def load_dataset(
    source: str,
    source_type: Literal['file','url','inline'] = 'file',
) -> schema.DatasetHandle:
    """Load data into a GE DataContext and return handle."""
    if source_type == 'file':
        df = pd.read_csv(Path(source))
    elif source_type == 'url':
        import requests
        txt = requests.get(source).text
        df = pd.read_csv(io.StringIO(txt))
    else:
        df = pd.read_csv(io.StringIO(source))
    handle = storage.DataStorage.add(df)
    return schema.DatasetHandle(handle=handle)
