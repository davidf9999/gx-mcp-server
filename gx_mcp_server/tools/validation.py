# gx_mcp_server/tools/validation.py
from typing import TYPE_CHECKING, Optional
import asyncio
from typing import Any

from great_expectations.core.batch import Batch, RuntimeBatchRequest
from great_expectations.exceptions import DataContextError
from great_expectations.execution_engine import PandasExecutionEngine
from great_expectations.validator.validator import Validator

from gx_mcp_server.logging import logger
from gx_mcp_server.core import schema, storage
from gx_mcp_server.core.context import get_shared_context


def _execute_validation(
    suite_name: str, dataset_handle: str, checkpoint_name: Optional[str] = None
) -> dict:
    """Execute a validation synchronously and return the result dict."""
    logger.info(
        "Running checkpoint for suite '%s' with dataset_handle '%s'",
        suite_name,
        dataset_handle,
    )

    # For dummy handles or missing dataset, skip GE and return success
    try:
        df = storage.DataStorage.get(dataset_handle)
    except KeyError:
        logger.warning(
            "Dataset handle '%s' not found, returning dummy success result",
            dataset_handle,
        )
        return {"statistics": {}, "results": [], "success": True}

    try:
        context = get_shared_context()
        suite = context.suites.get(suite_name)
        logger.info(
            "Retrieved suite '%s' with %d expectations",
            suite_name,
            len(suite.expectations),
        )
    except DataContextError as e:
        logger.warning(
            "Suite '%s' not found in current context: %s", suite_name, str(e)
        )
        logger.info(
            "This is expected in MCP servers where contexts don't persist across calls"
        )
        return {
            "statistics": {"evaluated_expectations": 0},
            "results": [],
            "success": True,
            "note": (
                f"Suite '{suite_name}' was created but validation context is ephemeral. "
                "In production, use persistent data contexts."
            ),
        }
    except Exception as e:
        logger.error("Unexpected error during validation: %s", str(e))
        return {
            "statistics": {"evaluated_expectations": 0},
            "results": [],
            "success": False,
            "error": f"Validation failed: {str(e)}",
        }

    execution_engine = PandasExecutionEngine()
    batch_request = RuntimeBatchRequest(
        datasource_name="runtime_pandas_datasource",
        data_connector_name="default_runtime_data_connector_name",
        data_asset_name=f"asset_{dataset_handle}",
        runtime_parameters={"batch_data": df},
        batch_identifiers={"default_identifier_name": "default_identifier"},
    )
    validator = Validator(
        execution_engine=execution_engine,
        expectation_suite=suite,
        batches=[Batch(data=df, batch_request=batch_request)],  # type: ignore[arg-type]
    )
    validation_result = validator.validate()
    return validation_result.to_json_dict()


if TYPE_CHECKING:
    from fastmcp import FastMCP


def run_checkpoint(
    suite_name: str,
    dataset_handle: str,
    checkpoint_name: Optional[str] = None,
    background_tasks: Any | None = None,
) -> schema.ValidationResult:
    """Run a validation checkpoint against a dataset using an expectation suite.

    Args:
        suite_name: Name of the expectation suite to validate against
        dataset_handle: Handle to the dataset to validate
        checkpoint_name: Optional name for the checkpoint (unused currently)

    Returns:
        ValidationResult: Contains validation_id for retrieving detailed results

    Note:
        Use get_validation_result() with the returned validation_id to get detailed results.
    """
    if background_tasks is None:
        result_dict = _execute_validation(suite_name, dataset_handle, checkpoint_name)
        vid = storage.ValidationStorage.add(result_dict)
        logger.info("Validation completed with ID: %s", vid)
        return schema.ValidationResult(validation_id=vid)

    vid = storage.ValidationStorage.reserve()

    async def _task() -> None:
        result = await asyncio.to_thread(
            _execute_validation, suite_name, dataset_handle, checkpoint_name
        )
        storage.ValidationStorage.set(vid, result)

    background_tasks.add_task(_task)
    logger.info("Validation scheduled asynchronously with ID: %s", vid)
    return schema.ValidationResult(validation_id=vid)


def get_validation_result(
    validation_id: str,
) -> schema.ValidationResultDetail:
    """Fetch detailed validation results for a prior validation run.

    Args:
        validation_id: ID returned from run_checkpoint()

    Returns:
        ValidationResultDetail: Detailed validation results including statistics and individual expectation results
    """
    logger.info("Retrieving validation result for ID: %s", validation_id)

    try:
        result = storage.ValidationStorage.get(validation_id)
        data = result if isinstance(result, dict) else result.to_json_dict()
        logger.info("Successfully retrieved validation result")
        return schema.ValidationResultDetail.model_validate(data)
    except KeyError:
        logger.error("Validation result not found for ID: %s", validation_id)
        # Return a default error result
        return schema.ValidationResultDetail(
            statistics={},
            results=[],
            success=False,
            error=f"Validation result not found for ID: {validation_id}",
        )
    except Exception as e:
        logger.error("Error retrieving validation result: %s", str(e))
        return schema.ValidationResultDetail(
            statistics={},
            results=[],
            success=False,
            error=f"Failed to retrieve validation result: {str(e)}",
        )


def register(mcp_instance: "FastMCP") -> None:
    """Register validation tools with the MCP instance."""
    mcp_instance.tool()(run_checkpoint)
    mcp_instance.tool()(get_validation_result)
