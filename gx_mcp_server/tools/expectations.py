from typing import Dict, Any
import great_expectations as gx
from gx_mcp_server import mcp
from gx_mcp_server.core import storage, schema


@mcp.tool()
def create_suite(
    suite_name: str,
    dataset_handle: str,
    profiler: bool = False,
) -> schema.SuiteHandle:
    """Create an ExpectationSuite, optionally profiled from dataset."""
    context = gx.get_context()
    suite = context.create_expectation_suite(suite_name, overwrite_existing=True)
    if profiler:
        # Only fetch df when profiling
        df = storage.DataStorage.get(dataset_handle)
        profiler_obj = gx.profile.UserConfigurableProfiler(
            profile_dataset=df,
            suite=suite,
        )
        suite = profiler_obj.build_suite()
        context.save_expectation_suite(suite)
    return schema.SuiteHandle(suite_name=suite_name)


@mcp.tool()
def add_expectation(
    suite_name: str,
    expectation_type: str,
    kwargs: Dict[str, Any],
) -> schema.ToolResponse:
    """Add a single expectation to suite."""
    context = gx.get_context()
    suite = context.get_expectation_suite(suite_name)
    suite.add_expectation(expectation_type=expectation_type, **kwargs)
    context.save_expectation_suite(suite)
    return schema.ToolResponse(success=True, message="Expectation added")


# Expose direct functions for tests
create_suite = create_suite.fn
add_expectation = add_expectation.fn
