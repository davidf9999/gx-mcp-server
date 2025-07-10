import os

import great_expectations as gx
from great_expectations.data_context import FileDataContext

from gx_mcp_server.tools.expectations import add_expectation, create_suite


def test_suite_and_expectation(tmp_path):
    ctx = FileDataContext._create(project_root_dir=tmp_path)
    os.environ["GX_HOME"] = ctx.root_directory
    suite = create_suite(suite_name="test", dataset_handle="dummy", profiler=False)
    assert suite.suite_name == "test"
    resp = add_expectation(
        suite_name="test",
        expectation_type="expect_column_values_to_not_be_null",
        kwargs={"column": "a"},
    )
    assert resp.success
    loaded = gx.get_context().suites.get("test")
    assert len(loaded.expectations) == 1
    del os.environ["GX_HOME"]
