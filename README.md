# Great Expectations MCP Server

> Expose Great Expectations data-quality checks as MCP tools for LLM agents.

[![PyPI version](https://img.shields.io/pypi/v/gx-mcp-server)](https://pypi.org/project/gx-mcp-server)
[![License](https://img.shields.io/github/license/davidf9999/gx-mcp-server)](LICENSE)
[![CI](https://github.com/davidf9999/gx-mcp-server/actions/workflows/cl.yaml/badge.svg)](https://github.com/davidf9999/gx-mcp-server/actions/workflows/cl.yaml)

## TL;DR

- **Install:** `uv sync && uv pip install -e .[dev]`
- **Run server:** `uv run python -m gx_mcp_server --http`
- **Try examples:** `uv run python scripts/run_examples.py`
- **Test:** `uv run pytest`
- **Default CSV limit:** 50 MB (`MCP_CSV_SIZE_LIMIT_MB` to change)

## Features

- Load CSV data from file, URL, or inline
- Define and modify ExpectationSuites
- Validate data and fetch detailed results
- Multiple transport modes: STDIO, HTTP, Inspector (GUI)

## Quickstart

```bash
uv sync
uv pip install -e ".[dev]"
cp .env.example .env  # (optional: add your OpenAI API key)
uv run python scripts/run_examples.py
```

## Usage

- **STDIO mode:** For desktop AI agents (default)
  ```bash
  uv run python -m gx_mcp_server
  ```

- **HTTP mode:** For browser and API clients
  ```bash
  uv run python -m gx_mcp_server --http
  ```

- **Inspector GUI:**
  ```bash
  npx @modelcontextprotocol/inspector
  # Connect to: http://localhost:8000/mcp/
  ```

## Configuring Maximum CSV File Size

The server limits CSV files to **50 MB** by default. Override with:
```bash
export MCP_CSV_SIZE_LIMIT_MB=200  # Allow up to 200 MB
uv run python -m gx_mcp_server --http
```
Allowed values: 1–1024 MB.

## Docker

To build and run with Docker (Python and uv included):

```bash
docker build -t gx-mcp-server .
docker run --rm -p 8000:8000 gx-mcp-server
```

Run the test suite inside the container:

```bash
docker run --rm gx-mcp-server uv run pytest
```

## Examples

- [`examples/basic_roundtrip.py`](examples/basic_roundtrip.py): minimal workflow demo
- [`examples/ai_expectation_roundtrip.py`](examples/ai_expectation_roundtrip.py): LLM-assisted suite creation demo

## Continuous Integration

All PRs and pushes are tested automatically via [GitHub Actions](https://github.com/davidf9999/gx-mcp-server/actions):
- Lint: `ruff`
- Type check: `mypy`
- Test: `pytest`

To check locally:
```bash
uv run pre-commit run --all-files
uv run ruff check .
uv run mypy gx_mcp_server/
uv run pytest
```

## Telemetry

Great Expectations sends anonymous usage data to `posthog.greatexpectations.io` by default.
Set `GX_ANALYTICS_ENABLED=false` to disable telemetry.

## Future Work & Known Limitations

- **No persistent storage:** Data is in-memory; lost on restart.
- **No authentication:** Do NOT expose HTTP to untrusted networks.
- **No URL restrictions:** Use only in trusted environments.
- **No resource cleanup:** Large/long sessions may use significant RAM.
- **Concurrency:** Blocking/serial; no job queue or async.
- **API may change:** Expect early-breaking changes.

## License & Contributing

MIT License. See [CONTRIBUTING.md](CONTRIBUTING.md) for how to help!