# gx_mcp_server/core/storage.py
import uuid
from collections import OrderedDict
from typing import Any, Dict

import pandas as pd

# in-memory stores
_df_store: Dict[str, pd.DataFrame] = OrderedDict()
_result_store: Dict[str, Any] = OrderedDict()


class DataStorage:
    @staticmethod
    def add(df: pd.DataFrame) -> str:
        handle = str(uuid.uuid4())
        _df_store[handle] = df
        return handle

    @staticmethod
    def get(handle: str) -> pd.DataFrame:
        return _df_store[handle]

    @staticmethod
    def get_handle_path(handle: str) -> str:
        path = f"/tmp/{handle}.csv"
        _df_store[handle].to_csv(path, index=False)
        return path


class ValidationStorage:
    @staticmethod
    def add(result) -> str:
        vid = str(uuid.uuid4())
        _result_store[vid] = result
        return vid

    @staticmethod
    def get(vid: str):
        return _result_store[vid]
