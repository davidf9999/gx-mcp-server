import pandas as pd

from gx_mcp_server.tools.datasets import load_dataset


def test_load_and_handle():
    df = pd.DataFrame({"a": [1, 2, 3]})
    csv = df.to_csv(index=False)
    # call the underlying function
    res = load_dataset(source=csv, source_type="inline")
    assert isinstance(res.handle, str)
