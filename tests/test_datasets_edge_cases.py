# tests/test_datasets_edge_cases.py
from gx_mcp_server.tools.datasets import load_dataset


def test_inline_limit_exceeded():
    # generate ~54 MB of dummy CSV text
    large = "col\n" + "1\n" * (27_000_000)
    res = load_dataset(source=large, source_type="inline")
    assert "error" in res
    assert "Inline CSV exceeds 50 MB" in res["error"]
