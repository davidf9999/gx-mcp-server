from gx_mcp_server.tools.validation import _run_checkpoint as run_checkpoint, _get_validation_result as get_validation_result

def test_checkpoint_flow():
    vid = run_checkpoint(suite_name='test', dataset_handle='dummy').validation_id
    detail = get_validation_result(validation_id=vid)
    assert hasattr(detail, 'success')
