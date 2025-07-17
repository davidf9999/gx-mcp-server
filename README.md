# Great Expectations MCP Server

> Expose Great Expectations data-quality checks as MCP tools for LLM agents.

[![PyPI version](https://img.shields.io/pypi/v/gx-mcp-server)](https://pypi.org/project/gx-mcp-server)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/gx-mcp-server)](https://pypi.org/project/gx-mcp-server)
[![Docker Hub](https://img.shields.io/docker/pulls/davidf9999/gx-mcp-server.svg)](https://hub.docker.com/r/davidf9999/gx-mcp-server)
[![License](https://img.shields.io/github/license/davidf9999/gx-mcp-server)](LICENSE)
[![CI](https://github.com/davidf9999/gx-mcp-server/actions/workflows/ci.yaml/badge.svg?branch=main)](https://github.com/davidf9999/gx-mcp-server/actions/workflows/ci.yaml)
[![Publish](https://github.com/davidf9999/gx-mcp-server/actions/workflows/publish.yaml/badge.svg)](https://github.com/davidf9999/gx-mcp-server/actions/workflows/publish.yaml)

## Motivation
 
Large Language Model (LLM) agents often need to interact with and validate data. Great Expectations is a powerful open-source tool for data quality, but it's not natively accessible to LLM agents. This server bridges that gap by exposing core Great Expectations functionality through the Model Context Protocol (MCP), allowing agents to:

- Programmatically load datasets from various sources.
- Define data quality rules (Expectations) on the fly.
- Run validation checks and interpret the results.
- Integrate robust data quality checks into their automated workflows.

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

## Metrics and Tracing

- Prometheus metrics exposed on `--metrics-port` (default **9090**).
- Enable OpenTelemetry tracing with `--trace`. When enabled, logs include
  `OTEL_RESOURCE_ATTRIBUTES` and spans are exported via OTLP.

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