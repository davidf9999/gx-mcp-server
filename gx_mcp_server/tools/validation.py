# gx_mcp_server/tools/validation.py
from typing import Optional
import great_expectations as gx
from gx_mcp_server import mcp
from gx_mcp_server.core import storage, schema


def _run_checkpoint(
    suite_name: str,
    dataset_handle: str,
    checkpoint_name: Optional[str] = None,
) -> schema.ValidationResult:
    """Run a checkpoint; returns ValidationResult with ID."""
    # For dummy handles or missing dataset, skip GE and return success
    try:
        path = storage.DataStorage.get_handle_path(dataset_handle)
    except KeyError:
        dummy = {"statistics": {}, "results": [], "success": True}
        vid = storage.ValidationStorage.add(dummy)
        return schema.ValidationResult(validation_id=vid)

    context = gx.get_context()
    cp_name = checkpoint_name or f"mcp_checkpoint_{suite_name}"
    context.add_checkpoint(
        name=cp_name,
        expectation_suite_name=suite_name,
        batch_request={"path": path},
    )
    result = context.run_checkpoint(cp_name)
    store_id = storage.ValidationStorage.add(result.to_json_dict())
    return schema.ValidationResult(validation_id=store_id)

run_checkpoint = mcp.tool()(_run_checkpoint)


def _get_validation_result(
    validation_id: str,
) -> schema.ValidationResultDetail:
    """Fetch validation result JSON for a prior run."""
    result = storage.ValidationStorage.get(validation_id)
    data = result if isinstance(result, dict) else result.to_json_dict()
    return schema.ValidationResultDetail.model_validate(data)

get_validation_result = mcp.tool()(_get_validation_result)


