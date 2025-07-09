# gx_mcp_server/tools/expectations.py
"""
MCP tools for managing Great Expectations suites and expectations.
"""

from typing import Any, Dict

import great_expectations as gx
from great_expectations.core import ExpectationSuite
from great_expectations.exceptions import DataContextError

from gx_mcp_server import logger, mcp
from gx_mcp_server.core import schema, storage


def _create_suite(
    suite_name: str,
    dataset_handle: str,
    profiler: bool = False,
) -> schema.SuiteHandle:
    """Create a named ExpectationSuite, optionally profiled from a dataset."""
    logger.info("Creating suite '%s' (profiler=%s)", suite_name, profiler)
    context = gx.get_context()

    # Initialize an empty suite
    suite = ExpectationSuite(suite_name)
    context.suites.add_or_update(suite)
    logger.info("Suite '%s' registered in context", suite_name)

    if profiler:
        # Fetch the DataFrame for profiling
        df = storage.DataStorage.get(dataset_handle)
        logger.info("Profiling dataset handle=%s", dataset_handle)
        profiler_obj = gx.profile.UserConfigurableProfiler(
            profile_dataset=df,
            suite=suite,
        )
        suite = profiler_obj.build_suite()
        context.suites.add_or_update(suite)
        logger.info("Suite '%s' updated with profiled expectations", suite_name)

    return schema.SuiteHandle(suite_name=suite_name)


# Register as an MCP tool
create_suite = mcp.tool()(_create_suite)


def _add_expectation(
    suite_name: str,
    expectation_type: str,
    kwargs: Dict[str, Any],
) -> schema.ToolResponse:
    """Add a single expectation to an existing suite (or create it)."""
    logger.info(
        "Adding expectation '%s' to suite '%s' with kwargs=%s",
        expectation_type,
        suite_name,
        kwargs,
    )
    context = gx.get_context()
    try:
        suite = context.suites.get(suite_name)
    except DataContextError:
        logger.warning("Suite '%s' not found, creating new one", suite_name)
        suite = ExpectationSuite(suite_name)
        context.suites.add_or_update(suite)

    # Instantiate the expectation and add it
    impl = gx.expectations.registry.get_expectation_impl(expectation_type)
    expectation = impl(**kwargs)
    suite.add_expectation(expectation)
    context.suites.add_or_update(suite)
    logger.info(
        "Expectation '%s' added to suite '%s'",
        expectation_type,
        suite_name,
    )
    return schema.ToolResponse(success=True, message="Expectation added")


# Register as an MCP tool
add_expectation = mcp.tool()(_add_expectation)
