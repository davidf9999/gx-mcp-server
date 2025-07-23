import asyncio
import pytest
from fastapi import BackgroundTasks

from gx_mcp_server.tools.expectations import create_suite, add_expectation
from gx_mcp_server.tools.datasets import load_dataset
from gx_mcp_server.tools.validation import run_checkpoint, get_validation_result


@pytest.mark.asyncio
async def test_concurrent_validations():
    create_suite(suite_name="async_suite", dataset_handle="dummy", profiler=False)
    add_expectation(
        suite_name="async_suite",
        expectation_type="expect_column_to_exist",
        kwargs={"column": "a"},
    )

    handle1 = load_dataset("a\n1", source_type="inline").handle
    handle2 = load_dataset("a\n2", source_type="inline").handle

    bgs = [BackgroundTasks(), BackgroundTasks()]
    results = await asyncio.gather(
        asyncio.to_thread(
            run_checkpoint, "async_suite", handle1, background_tasks=bgs[0]
        ),
        asyncio.to_thread(
            run_checkpoint, "async_suite", handle2, background_tasks=bgs[1]
        ),
    )

    await asyncio.gather(*(bg() for bg in bgs))

    for res in results:
        detail = get_validation_result(res.validation_id)
        assert detail.success is True
