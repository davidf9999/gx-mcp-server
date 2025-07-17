from gx_mcp_server.tools.datasets import load_dataset
from gx_mcp_server.tools.expectations import add_expectation, create_suite
from gx_mcp_server.tools.validation import get_validation_result, run_checkpoint
from gx_mcp_server.core.storage import DataStorage


def test_load_dataset():
    csv_data = "col1,col2\n1,a\n2,b"
    result = load_dataset(source=csv_data, source_type="inline", max_rows=1)
    assert result.handle is not None
    df = DataStorage.get(result.handle)
    assert len(df) == 1


def test_create_suite():
    suite_name = "test_suite"
    dataset_handle = "dummy_handle"
    result = create_suite(suite_name=suite_name, dataset_handle=dataset_handle)
    assert result.suite_name == suite_name


def test_add_expectation():
    suite_name = "test_suite_add_exp"
    dataset_handle = "dummy_handle"
    create_suite(suite_name=suite_name, dataset_handle=dataset_handle)
    result = add_expectation(
        suite_name=suite_name,
        expectation_type="expect_column_to_exist",
        kwargs={"column": "col1"},
    )
    assert result.success is True


def test_run_checkpoint():
    suite_name = "test_suite_checkpoint"
    dataset_handle = "dummy_handle"
    create_suite(suite_name=suite_name, dataset_handle=dataset_handle)
    result = run_checkpoint(suite_name=suite_name, dataset_handle=dataset_handle)
    assert result.validation_id is not None


def test_get_validation_result():
    suite_name = "test_suite_get_result"
    dataset_handle = "dummy_handle"
    create_suite(suite_name=suite_name, dataset_handle=dataset_handle)
    validation_result = run_checkpoint(
        suite_name=suite_name, dataset_handle=dataset_handle
    )
    result = get_validation_result(validation_id=validation_result.validation_id)
    assert result.success is True
