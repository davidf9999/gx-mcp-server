import pandas as pd
import pytest

from gx_mcp_server.tools.datasets import load_dataset
from gx_mcp_server.core.storage import DataStorage


def test_load_and_handle():
    df = pd.DataFrame({"a": [1, 2, 3]})
    csv = df.to_csv(index=False)
    # call the underlying function
    res = load_dataset(source=csv, source_type="inline")
    assert isinstance(res.handle, str)


def test_load_empty_csv():
    """Test loading an empty CSV file."""
    empty_csv = ""
    with pytest.raises(Exception):
        load_dataset(source=empty_csv, source_type="inline")


def test_load_header_only_csv():
    """Test loading a CSV with only a header."""
    header_only_csv = "col1,col2"
    res = load_dataset(source=header_only_csv, source_type="inline")
    assert isinstance(res.handle, str)
    # Verify that the dataframe is empty but has the correct columns
    df = DataStorage.get(res.handle)
    assert df.empty
    assert list(df.columns) == ["col1", "col2"]
