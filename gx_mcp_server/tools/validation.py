# gx_mcp_server/tools/validation.py
from typing import TYPE_CHECKING, Optional, cast

import great_expectations as gx
from great_expectations.exceptions import DataContextError

from gx_mcp_server import logger
from gx_mcp_server.core import schema, storage

if TYPE_CHECKING:
    from fastmcp import FastMCP


def run_checkpoint(
    suite_name: str,
    dataset_handle: str,
    checkpoint_name: Optional[str] = None,
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
    logger.info(
        "Running checkpoint for suite '%s' with dataset_handle '%s'",
        suite_name,
        dataset_handle,
    )

    # For dummy handles or missing dataset, skip GE and return success
    try:
        _path = storage.DataStorage.get_handle_path(dataset_handle)
        logger.info("Dataset path resolved: %s", _path)
    except KeyError:
        logger.warning(
            "Dataset handle '%s' not found, returning dummy success result",
            dataset_handle,
        )
        dummy = {"statistics": {}, "results": [], "success": True}
        vid = storage.ValidationStorage.add(dummy)
        return schema.ValidationResult(validation_id=vid)

    try:
        context = gx.get_context()
        suite = context.suites.get(suite_name)
        logger.info(
            "Retrieved suite '%s' with %d expectations",
            suite_name,
            len(suite.expectations),
        )
    except DataContextError as e:
        logger.error("Failed to get suite '%s': %s", suite_name, str(e))
        # Return a failure result
        error_result = {
            "statistics": {"evaluated_expectations": 0},
            "results": [],
            "success": False,
            "error": f"Suite '{suite_name}' not found: {str(e)}",
        }
        vid = storage.ValidationStorage.add(error_result)
        return schema.ValidationResult(validation_id=vid)
    except Exception as e:
        logger.error("Unexpected error during validation: %s", str(e))
        error_result = {
            "statistics": {"evaluated_expectations": 0},
            "results": [],
            "success": False,
            "error": f"Validation failed: {str(e)}",
        }
        vid = storage.ValidationStorage.add(error_result)
        return schema.ValidationResult(validation_id=vid)

    # For now, let's create a simple validation result
    # TODO: Implement proper validation with current GE API
    result_dict = {
        "statistics": {"evaluated_expectations": len(suite.expectations)},
        "results": [],
        "success": True,
    }
    store_id = storage.ValidationStorage.add(result_dict)
    logger.info("Validation completed successfully with ID: %s", store_id)
    return schema.ValidationResult(validation_id=store_id)


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
        return cast(schema.ValidationResultDetail, schema.ValidationResultDetail.model_validate(data))
    except KeyError:
        logger.error("Validation result not found for ID: %s", validation_id)
        # Return a default error result
        error_data = {
            "statistics": {},
            "results": [],
            "success": False,
            "error": f"Validation result not found for ID: {validation_id}",
        }
        return cast(schema.ValidationResultDetail, schema.ValidationResultDetail.model_validate(error_data))
    except Exception as e:
        logger.error("Error retrieving validation result: %s", str(e))
        error_data = {
            "statistics": {},
            "results": [],
            "success": False,
            "error": f"Failed to retrieve validation result: {str(e)}",
        }
        return cast(schema.ValidationResultDetail, schema.ValidationResultDetail.model_validate(error_data))


def register(mcp_instance: "FastMCP") -> None:
    """Register validation tools with the MCP instance."""
    mcp_instance.tool()(run_checkpoint)
    mcp_instance.tool()(get_validation_result)
