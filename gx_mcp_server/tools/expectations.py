from typing import Dict, Any
import great_expectations as gx
from gx_mcp_server import mcp
from gx_mcp_server.core import storage, schema


def _create_suite(
    suite_name: str,
    dataset_handle: str,
    profiler: bool = False,
) -> schema.SuiteHandle:
    """Create an ExpectationSuite, optionally profiled from dataset."""
    context = gx.get_context()
    suite = gx.ExpectationSuite(name=suite_name)
    suite = context.suites.add_or_update(suite)
    if profiler:
        # Only fetch df when profiling
        df = storage.DataStorage.get(dataset_handle)
        profiler_obj = gx.profile.UserConfigurableProfiler(
            profile_dataset=df,
            suite=suite,
        )
        suite = profiler_obj.build_suite()
        context.suites.add_or_update(suite)
    return schema.SuiteHandle(suite_name=suite_name)

create_suite = mcp.tool()(_create_suite)

def _add_expectation(
    suite_name: str,
    expectation_type: str,
    kwargs: Dict[str, Any],
) -> schema.ToolResponse:
    """Add a single expectation to suite."""
    context = gx.get_context()
    try:
        suite = context.suites.get(suite_name)
    except:
        # Create suite if it doesn't exist
        suite = gx.ExpectationSuite(name=suite_name)
        suite = context.suites.add_or_update(suite)
    expectation = gx.expectations.registry.get_expectation_impl(expectation_type)(**kwargs)
    suite.add_expectation(expectation)
    context.suites.add_or_update(suite)
    return schema.ToolResponse(success=True, message="Expectation added")

add_expectation = mcp.tool()(_add_expectation)


