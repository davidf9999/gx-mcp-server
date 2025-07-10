from gx_mcp_server.tools.datasets import _load_dataset
from gx_mcp_server.tools.expectations import _add_expectation, _create_suite
from gx_mcp_server.tools.validation import (_get_validation_result,
                                            _run_checkpoint)


def test_load_dataset():
    csv_data = "col1,col2\n1,a\n2,b"
    result = _load_dataset(source=csv_data, source_type="inline")
    assert result.handle is not None


def test_create_suite():
    suite_name = "test_suite"
    dataset_handle = "dummy_handle"
    result = _create_suite(suite_name=suite_name, dataset_handle=dataset_handle)
    assert result.suite_name == suite_name


def test_add_expectation():
    suite_name = "test_suite_add_exp"
    dataset_handle = "dummy_handle"
    _create_suite(suite_name=suite_name, dataset_handle=dataset_handle)
    result = _add_expectation(
        suite_name=suite_name,
        expectation_type="expect_column_to_exist",
        kwargs={"column": "col1"},
    )
    assert result.success is True


def test_run_checkpoint():
    suite_name = "test_suite_checkpoint"
    dataset_handle = "dummy_handle"
    _create_suite(suite_name=suite_name, dataset_handle=dataset_handle)
    result = _run_checkpoint(suite_name=suite_name, dataset_handle=dataset_handle)
    assert result.validation_id is not None


def test_get_validation_result():
    suite_name = "test_suite_get_result"
    dataset_handle = "dummy_handle"
    _create_suite(suite_name=suite_name, dataset_handle=dataset_handle)
    validation_result = _run_checkpoint(
        suite_name=suite_name, dataset_handle=dataset_handle
    )
    result = _get_validation_result(validation_id=validation_result.validation_id)
    assert result.success is True
