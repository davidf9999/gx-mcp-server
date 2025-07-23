from gx_mcp_server.tools.expectations import add_expectation, create_suite


def test_suite_and_expectation(tmp_path):
    # Test creating suite and adding expectation
    suite = create_suite(suite_name="test", dataset_handle="dummy", profiler=False)
    assert suite.suite_name == "test"

    # Test adding expectation to the suite
    resp = add_expectation(
        suite_name="test",
        expectation_type="expect_column_values_to_not_be_null",
        kwargs={"column": "a"},
    )
    assert resp.success
