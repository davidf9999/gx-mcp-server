from gx_mcp_server.tools.expectations import _create_suite as create_suite, _add_expectation as add_expectation

def test_suite_and_expectation():
    suite = create_suite(suite_name='test', dataset_handle='dummy', profiler=False)
    assert suite.suite_name == 'test'
    resp = add_expectation(suite_name='test', expectation_type='expect_column_values_to_not_be_null', kwargs={'column':'a'})
    assert resp.success
