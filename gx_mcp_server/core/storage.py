# gx_mcp_server/core/storage.py
"""Storage backends for datasets and validation results."""

from __future__ import annotations

import threading
import uuid
from collections import OrderedDict
from typing import Any

import pandas as pd

_MAX_ITEMS = 100

# ---------------------------------------------------------------------------
# In-memory implementation
# ---------------------------------------------------------------------------
_df_store: OrderedDict[str, pd.DataFrame] = OrderedDict()
_result_store: OrderedDict[str, Any] = OrderedDict()
_df_lock = threading.Lock()
_result_lock = threading.Lock()


class _InMemoryDataStorage:
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


class _InMemoryValidationStorage:
    @staticmethod
    def add(result: Any) -> str:
        vid = str(uuid.uuid4())
        with _result_lock:
            if len(_result_store) >= _MAX_ITEMS:
                _result_store.popitem(last=False)
            _result_store[vid] = result
        return vid

    @classmethod
    def reserve(cls) -> str:
        """Reserve an ID for an asynchronous validation run."""
        vid = str(uuid.uuid4())
        with _result_lock:
            if len(_result_store) >= _MAX_ITEMS:
                _result_store.popitem(last=False)
            _result_store[vid] = {"status": "pending"}
        return vid

    @classmethod
    def set(cls, vid: str, result: Any) -> None:
        """Store a validation result for a pre-reserved ID."""
        with _result_lock:
            _result_store[vid] = result

    @classmethod
    def get(cls, vid: str) -> Any:
        """Retrieve a stored validation result by ID."""
        with _result_lock:
            return _result_store[vid]


# ---------------------------------------------------------------------------
# Dynamic backend dispatch
# ---------------------------------------------------------------------------
_data_backend: type[_InMemoryDataStorage] | Any = _InMemoryDataStorage
_validation_backend: type[_InMemoryValidationStorage] | Any = _InMemoryValidationStorage


def configure_storage_backend(uri: str) -> None:
    """Configure storage backend based on URI."""
    global _data_backend, _validation_backend

    if uri.startswith("sqlite:///"):
        from gx_mcp_server.storage import sqlite_backend

        sqlite_backend.initialize(uri)
        _data_backend = sqlite_backend.DataStorage
        _validation_backend = sqlite_backend.ValidationStorage
    else:
        _data_backend = _InMemoryDataStorage
        _validation_backend = _InMemoryValidationStorage


class DataStorage:
    """Facade for the configured DataStorage backend."""

    @staticmethod
    def add(df: pd.DataFrame) -> str:
        return _data_backend.add(df)

    @staticmethod
    def get(handle: str) -> pd.DataFrame:
        return _data_backend.get(handle)

    @staticmethod
    def get_handle_path(handle: str) -> str:
        return _data_backend.get_handle_path(handle)


class ValidationStorage:
    """Facade for the configured ValidationStorage backend."""

    @staticmethod
    def add(result: Any) -> str:
        return _validation_backend.add(result)

    @staticmethod
    def get(vid: str) -> Any:
        return _validation_backend.get(vid)

    @staticmethod
    def reserve() -> str:
        """Reserve an ID for an asynchronous validation run."""
        return _validation_backend.reserve()

    @staticmethod
    def set(vid: str, result: Any) -> None:
        """Store a validation result for a pre-reserved ID."""
        _validation_backend.set(vid, result)
