# tests/test_error_handling.py
import uuid
import pandas as pd
from gx_mcp_server.tools.datasets import load_dataset
from gx_mcp_server.tools.expectations import add_expectation, create_suite
from gx_mcp_server.tools.validation import get_validation_result
from gx_mcp_server.core.storage import DataStorage

def test_load_malformed_csv():
    """Test loading a malformed CSV to ensure it's handled."""
    # This CSV has an incorrect number of columns in the second data row
    malformed_csv = "col1,col2\n1,a\n2"
    res = load_dataset(source=malformed_csv, source_type="inline")
    df = DataStorage.get(res.handle)
    # Pandas should parse this into a two-row dataframe, with the second row having a NaN value
    assert len(df) == 2
    # Pandas represents missing values in CSVs as NaN (float) rather than
    # ``pd.NA``. Use ``pd.isna`` to cover both cases to avoid strict identity
    # checks failing when a float NaN is returned.
    assert pd.isna(df.iloc[1][1])

def test_get_non_existent_validation_result():
    """Test fetching a validation result with a non-existent ID."""
    fake_id = str(uuid.uuid4())
    result = get_validation_result(validation_id=fake_id)
    assert result.success is False
    assert result.error is not None
    assert "not found" in result.error.lower()

def test_add_unsupported_expectation():
    """Test adding an expectation with an unsupported type."""
    suite_name = "test_suite_unsupported_exp"
    create_suite(suite_name=suite_name, dataset_handle="dummy")
    # Using a non-existent expectation type should raise an exception from GX
    res = add_expectation(
        suite_name=suite_name,
        expectation_type="expect_this_to_fail_miserably",
        kwargs={"column": "col1"},
    )
    assert not res.success
    assert "failed" in res.message.lower() or "not found" in res.message.lower()
