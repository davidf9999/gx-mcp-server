import uuid
from collections import OrderedDict
from typing import Dict, Any
import pandas as pd

df_store: Dict[str, pd.DataFrame] = OrderedDict()
result_store: Dict[str, Any] = OrderedDict()

class DataStorage:
    @staticmethod
    def add(df: pd.DataFrame) -> str:
        handle = str(uuid.uuid4())
        df_store[handle] = df
        return handle
    @staticmethod
    def get(handle: str) -> pd.DataFrame:
        return df_store[handle]
    @staticmethod
    def get_handle_path(handle: str) -> str:
        path = f'/tmp/{handle}.csv'
        df_store[handle].to_csv(path, index=False)
        return path

class ValidationStorage:
    @staticmethod
    def add(result) -> str:
        vid = str(uuid.uuid4())
        result_store[vid] = result
        return vid
    @staticmethod
    def get(vid: str):
        return result_store[vid]
