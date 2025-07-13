# tests/test_datasets_edge_cases.py
import pytest
from gx_mcp_server.tools.datasets import load_dataset


def test_inline_limit_exceeded():
    # generate ~54 MB of dummy CSV text
    large = "col\n" + "1\n" * (27_000_000)
    with pytest.raises(ValueError, match="Inline CSV exceeds 50 MB"):
        load_dataset(source=large, source_type="inline")
