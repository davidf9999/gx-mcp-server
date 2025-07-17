import pandas as pd
from gx_mcp_server.core import storage


def test_sqlite_persistence(tmp_path):
    db_path = tmp_path / "gx.db"
    storage.configure_storage_backend(f"sqlite:///{db_path}")

    df = pd.DataFrame({"a": [1, 2]})
    handle = storage.DataStorage.add(df)
    vid = storage.ValidationStorage.add({"ok": True})

    # Reinitialize to simulate a new process
    storage.configure_storage_backend(f"sqlite:///{db_path}")

    df_loaded = storage.DataStorage.get(handle)
    assert df_loaded.equals(df)

    result_loaded = storage.ValidationStorage.get(vid)
    assert result_loaded == {"ok": True}
