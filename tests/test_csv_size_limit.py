from gx_mcp_server.tools.datasets import load_dataset, get_csv_size_limit_bytes


def make_csv_with_size(byte_size):
    # Minimum CSV: header + lines of 'a\n' (2 bytes/line)
    header = "col\n"
    data_bytes = byte_size - len(header.encode("utf-8"))
    num_lines = max(1, data_bytes // 2)
    lines = ("a\n" * num_lines)[:data_bytes]
    return header + lines


def test_default_limit_inline(monkeypatch):
    # Should reject ~51MB inline by default
    csv = make_csv_with_size(51 * 1024 * 1024)
    res = load_dataset(csv, source_type="inline")
    assert "error" in res
    assert "exceeds 50 MB" in res["error"]


def test_env_override_increases_limit(monkeypatch):
    monkeypatch.setenv("MCP_CSV_SIZE_LIMIT_MB", "60")
    csv = make_csv_with_size(55 * 1024 * 1024)
    # Should succeed (limit is 60MB)
    handle = load_dataset(csv, source_type="inline")
    assert handle.handle


def test_env_override_too_low(monkeypatch):
    # Values < 1 should fall back to default (50)
    monkeypatch.setenv("MCP_CSV_SIZE_LIMIT_MB", "0")
    csv = make_csv_with_size(51 * 1024 * 1024)
    res = load_dataset(csv, source_type="inline")
    assert "error" in res
    assert "exceeds 50 MB" in res["error"]


def test_env_override_too_high(monkeypatch):
    # Values > 1024 should fall back to default (50)
    monkeypatch.setenv("MCP_CSV_SIZE_LIMIT_MB", "9999")
    csv = make_csv_with_size(51 * 1024 * 1024)
    res = load_dataset(csv, source_type="inline")
    assert "error" in res
    assert "exceeds 50 MB" in res["error"]


def test_env_override_non_int(monkeypatch):
    # Non-int values should fall back to default
    monkeypatch.setenv("MCP_CSV_SIZE_LIMIT_MB", "hello")
    csv = make_csv_with_size(51 * 1024 * 1024)
    res = load_dataset(csv, source_type="inline")
    assert "error" in res
    assert "exceeds 50 MB" in res["error"]


def test_get_csv_size_limit_bytes_default(monkeypatch):
    monkeypatch.delenv("MCP_CSV_SIZE_LIMIT_MB", raising=False)
    assert get_csv_size_limit_bytes() == 50 * 1024 * 1024


def test_get_csv_size_limit_bytes_valid(monkeypatch):
    monkeypatch.setenv("MCP_CSV_SIZE_LIMIT_MB", "123")
    assert get_csv_size_limit_bytes() == 123 * 1024 * 1024


def test_get_csv_size_limit_bytes_invalid(monkeypatch):
    monkeypatch.setenv("MCP_CSV_SIZE_LIMIT_MB", "-10")
    assert get_csv_size_limit_bytes() == 50 * 1024 * 1024
    monkeypatch.setenv("MCP_CSV_SIZE_LIMIT_MB", "abc")
    assert get_csv_size_limit_bytes() == 50 * 1024 * 1024
    monkeypatch.setenv("MCP_CSV_SIZE_LIMIT_MB", "2048")
    assert get_csv_size_limit_bytes() == 50 * 1024 * 1024
