import os
import sqlite3
import threading
import uuid
import pickle
from typing import Any

import pandas as pd

_conn: sqlite3.Connection | None = None
_db_path: str | None = None
_lock = threading.Lock()
_MAX_ITEMS = 100


def initialize(uri: str) -> None:
    """Initialize the SQLite backend given a URI like sqlite:///path/to/db."""
    global _conn, _db_path
    path = uri[len("sqlite:///") :]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    _db_path = path
    if _conn is not None:
        _conn.close()
    _conn = sqlite3.connect(path, check_same_thread=False)
    _conn.execute(
        "CREATE TABLE IF NOT EXISTS datasets (id TEXT PRIMARY KEY, data BLOB, created INTEGER)"
    )
    _conn.execute(
        "CREATE TABLE IF NOT EXISTS validations (id TEXT PRIMARY KEY, data BLOB, created INTEGER)"
    )
    _conn.commit()


def _get_conn() -> sqlite3.Connection:
    if _conn is None:
        if _db_path is None:
            raise RuntimeError("SQLite backend not initialized")
        initialize(f"sqlite:///{_db_path}")
    assert _conn is not None
    return _conn


class DataStorage:
    @staticmethod
    def add(df: pd.DataFrame) -> str:
        handle = str(uuid.uuid4())
        blob = pickle.dumps(df)
        with _lock:
            conn = _get_conn()
            conn.execute(
                "INSERT INTO datasets (id, data, created) VALUES (?, ?, strftime('%s','now'))",
                (handle, blob),
            )
            conn.commit()
            count = conn.execute("SELECT COUNT(*) FROM datasets").fetchone()[0]
            if count > _MAX_ITEMS:
                to_delete = conn.execute(
                    "SELECT id FROM datasets ORDER BY created ASC LIMIT ?",
                    (count - _MAX_ITEMS,),
                ).fetchall()
                conn.executemany("DELETE FROM datasets WHERE id = ?", to_delete)
                conn.commit()
        return handle

    @staticmethod
    def get(handle: str) -> pd.DataFrame:
        conn = _get_conn()
        row = conn.execute("SELECT data FROM datasets WHERE id=?", (handle,)).fetchone()
        if row is None:
            raise KeyError(handle)
        return pickle.loads(row[0])

    @staticmethod
    def get_handle_path(handle: str) -> str:
        df = DataStorage.get(handle)
        path = f"/tmp/{handle}.csv"
        df.to_csv(path, index=False)
        return path


class ValidationStorage:
    @staticmethod
    def add(result: Any) -> str:
        vid = str(uuid.uuid4())
        blob = pickle.dumps(result)
        with _lock:
            conn = _get_conn()
            conn.execute(
                "INSERT INTO validations (id, data, created) VALUES (?, ?, strftime('%s','now'))",
                (vid, blob),
            )
            conn.commit()
            count = conn.execute("SELECT COUNT(*) FROM validations").fetchone()[0]
            if count > _MAX_ITEMS:
                to_delete = conn.execute(
                    "SELECT id FROM validations ORDER BY created ASC LIMIT ?",
                    (count - _MAX_ITEMS,),
                ).fetchall()
                conn.executemany("DELETE FROM validations WHERE id = ?", to_delete)
                conn.commit()
        return vid

    @staticmethod
    def get(vid: str) -> Any:
        conn = _get_conn()
        row = conn.execute("SELECT data FROM validations WHERE id=?", (vid,)).fetchone()
        if row is None:
            raise KeyError(vid)
        return pickle.loads(row[0])
