import pytest

from gx_mcp_server.core.context import get_shared_context, reset_context


@pytest.fixture(autouse=True)
def shared_gx_context():
    """Ensure a clean GX context for each test."""
    get_shared_context()  # Initialize context
    yield
    reset_context()  # Cleanup after test
