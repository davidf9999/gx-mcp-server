# gx_mcp_server/core/storage.py
import uuid
from collections import OrderedDict
from typing import Any
import threading

import pandas as pd

# in-memory stores
_df_store: OrderedDict[str, pd.DataFrame] = OrderedDict()
_result_store: OrderedDict[str, Any] = OrderedDict()
_df_lock = threading.Lock()
_result_lock = threading.Lock()
_MAX_ITEMS = 100


class DataStorage:
    @staticmethod
    def add(df: pd.DataFrame) -> str:
        handle = str(uuid.uuid4())
        with _df_lock:
            if len(_df_store) >= _MAX_ITEMS:
                _df_store.popitem(last=False)
            _df_store[handle] = df
        return handle

    @staticmethod
    def get(handle: str) -> pd.DataFrame:
        with _df_lock:
            return _df_store[handle]

    @staticmethod
    def get_handle_path(handle: str) -> str:
        path = f"/tmp/{handle}.csv"
        with _df_lock:
            _df_store[handle].to_csv(path, index=False)
        return path


class ValidationStorage:
    @staticmethod
    def add(result: Any) -> str:
        vid = str(uuid.uuid4())
        with _result_lock:
            if len(_result_store) >= _MAX_ITEMS:
                _result_store.popitem(last=False)
            _result_store[vid] = result
        return vid

    @staticmethod
    def reserve() -> str:
        """Reserve an ID for an asynchronous validation run."""
        vid = str(uuid.uuid4())
        with _result_lock:
            if len(_result_store) >= _MAX_ITEMS:
                _result_store.popitem(last=False)
            _result_store[vid] = {"status": "pending"}
        return vid

    @staticmethod
    def set(vid: str, result: Any) -> None:
        """Store a validation result for a pre-reserved ID."""
        with _result_lock:
            _result_store[vid] = result

    @staticmethod
    def get(vid: str) -> Any:
        with _result_lock:
            return _result_store[vid]
