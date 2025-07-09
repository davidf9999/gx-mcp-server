from typing import Optional
import great_expectations as gx
from fastmcp import tool

from gx_mcp_server import mcp
from gx_mcp_server.core import storage, schema

@tool(mcp)
def run_checkpoint(
    suite_name: str,
    dataset_handle: str,
    checkpoint_name: Optional[str] = None,
) -> schema.ValidationResult:
    """Run a checkpoint against the dataset and return result ID."""
    context = gx.get_context()
    if not checkpoint_name:
        checkpoint_name = f'mcp_checkpoint_{suite_name}'
        context.add_checkpoint(
            name=checkpoint_name,
            expectation_suite_name=suite_name,
            batch_request={'path': storage.DataStorage.get_handle_path(dataset_handle)},
        )
    result = context.run_checkpoint(checkpoint_name)
    store_id = storage.ValidationStorage.add(result)
    return schema.ValidationResult(validation_id=store_id)

@tool(mcp)
def get_validation_result(
    validation_id: str,
) -> schema.ValidationResultDetail:
    """Fetch validation result JSON for a prior run."""
    result = storage.ValidationStorage.get(validation_id)
    return schema.ValidationResultDetail.parse_obj(result.to_json_dict())
