# tests/test_parallel_clients.py
import pytest
import asyncio
import threading
from gx_mcp_server.core.context import get_shared_context, reset_context
from gx_mcp_server.tools.expectations import create_suite, add_expectation


@pytest.mark.asyncio
async def test_concurrent_suite_creation():
    reset_context()

    def client_task(name):
        # each “client” creates its own suite
        create_suite(suite_name=name, dataset_handle="dummy", profiler=False)

    # Run two clients concurrently
    await asyncio.gather(
        asyncio.to_thread(client_task, "suite_A"),
        asyncio.to_thread(client_task, "suite_B"),
    )

    # After both tasks are done, get the final list of suites
    final_suites = [s.name for s in get_shared_context().suites.all()]

    # Both clients saw both suites, because context is shared
    assert "suite_A" in final_suites
    assert "suite_B" in final_suites


@pytest.mark.asyncio
async def test_race_condition_on_init(monkeypatch):
    reset_context()
    inits = 0

    # Monkey-patch the get_context call to count initializations
    import great_expectations as gx

    original = gx.get_context

    def counting_get_context(*args, **kwargs):
        nonlocal inits
        inits += 1
        return original(*args, **kwargs)

    monkeypatch.setattr(gx, "get_context", counting_get_context)

    # Use actual threads to test the lock
    threads = [threading.Thread(target=get_shared_context) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # If unguarded, you may see inits > 1
    assert inits == 1, "Context was initialized more than once!"


@pytest.mark.asyncio
async def test_concurrent_expectation_addition():
    reset_context()
    create_suite(suite_name="test_suite", dataset_handle="dummy", profiler=False)

    def client_task(col):
        # each “client” adds an expectation to the same suite
        add_expectation(
            suite_name="test_suite",
            expectation_type="expect_column_to_exist",
            kwargs={"column": col},
        )

    # Run two clients concurrently
    await asyncio.gather(
        asyncio.to_thread(client_task, "col_A"),
        asyncio.to_thread(client_task, "col_B"),
    )

    # After both tasks are done, get the final suite
    final_suite = get_shared_context().suites.get("test_suite")

    # Both clients saw both expectations, because context is shared
    assert len(final_suite.expectations) == 2
    assert {e.configuration.kwargs["column"] for e in final_suite.expectations} == {
        "col_A",
        "col_B",
    }
