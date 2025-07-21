# Great Expectations MCP Server

> Expose Great Expectations data-quality checks as MCP tools for LLM agents.

[![PyPI version](https://img.shields.io/pypi/v/gx-mcp-server)](https://pypi.org/project/gx-mcp-server)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/gx-mcp-server)](https://pypi.org/project/gx-mcp-server)
[![Docker Hub](https://img.shields.io/docker/pulls/davidf9999/gx-mcp-server.svg)](https://hub.docker.com/r/davidf9999/gx-mcp-server)
[![License](https://img.shields.io/github/license/davidf9999/gx-mcp-server)](LICENSE)
[![CI](https://github.com/davidf9999/gx-mcp-server/actions/workflows/ci.yaml/badge.svg?branch=dev)](https://github.com/davidf9999/gx-mcp-server/actions/workflows/ci.yaml)
[![Publish](https://github.com/davidf9999/gx-mcp-server/actions/workflows/publish.yaml/badge.svg)](https://github.com/davidf9999/gx-mcp-server/actions/workflows/publish.yaml)

## Motivation
 
Large Language Model (LLM) agents often need to interact with and validate data. Great Expectations is a powerful open-source tool for data quality, but it's not natively accessible to LLM agents. This server bridges that gap by exposing core Great Expectations functionality through the Model Context Protocol (MCP), allowing agents to:

- Programmatically load datasets from various sources.
- Define data quality rules (Expectations) on the fly.
- Run validation checks and interpret the results.
- Integrate robust data quality checks into their automated workflows.

## TL;DR

- **Install:** `just install`
- **Run server:** `just serve`
- **Try examples:** `just run-examples`
- **Test:** `just test`
- **Lint and type-check:** `just ci`
- **Default CSV limit:** 50 MB (`MCP_CSV_SIZE_LIMIT_MB` to change)

## Features

- Load CSV data from file, URL, or inline
- Load tables from Snowflake or BigQuery using URI prefixes
- Define and modify ExpectationSuites
- Validate data and fetch detailed results
- Multiple transport modes: STDIO, HTTP, Inspector (GUI)

## Quickstart

```bash
just install
cp .env.example .env  # (optional: add your OpenAI API key)
just run-examples
```

## Usage

- **STDIO mode:** For desktop AI agents (default)
  ```bash
  uv run python -m gx_mcp_server
  ```

- **HTTP mode:** For browser and API clients
```bash
just serve
# add basic auth (e.g., user "admin" with password "secret")
uv run python -m gx_mcp_server --http --basic-auth admin:secret
```

*Requests per minute limit*
```bash
uv run python -m gx_mcp_server --http --rate-limit 30
```
Default is 60 requests per minute.

- **HTTP mode (localhost only):**
  ```bash
  uv run python -m gx_mcp_server --http --host 127.0.0.1
  ```

- **Inspector GUI:**
  ```bash
  uv run python -m gx_mcp_server --inspect [--inspector-auth <token>]
  npx @modelcontextprotocol/inspector
  # Connect to: http://localhost:8000/mcp/  # append ?token=<token> if auth enabled
  ```

## Configuring Maximum CSV File Size

The server limits CSV files to **50 MB** by default. Override with:
```bash
export MCP_CSV_SIZE_LIMIT_MB=200  # Allow up to 200 MB
just serve
```
Allowed values: 1–1024 MB.

## Warehouse Connectors

Install extras to enable Snowflake or BigQuery support:

```bash
uv pip install -e .[snowflake]
uv pip install -e .[bigquery]
```

Then load tables directly using URIs:

```python
load_dataset("snowflake://user:pass@account/db/schema/table?warehouse=WH")
load_dataset("bigquery://my-project/dataset/table")
```

`load_dataset` automatically detects these prefixes and delegates to the
appropriate connector.

## Metrics and Tracing

- Prometheus metrics exposed on `--metrics-port` (default **9090**).
- Enable OpenTelemetry tracing with `--trace`. When enabled, logs include
  `OTEL_RESOURCE_ATTRIBUTES` and spans are exported via OTLP.

## Docker

To build and run with Docker (Python and uv included):

```bash
just docker-build
just docker-run
```

Run the test suite inside the container:

```bash
just docker-test
```

## Examples

- [`examples/basic_roundtrip.py`](examples/basic_roundtrip.py): minimal workflow demo
- [`examples/ai_expectation_roundtrip.py`](examples/ai_expectation_roundtrip.py): LLM-assisted suite creation demo

## Continuous Integration

All PRs and pushes are tested automatically via [GitHub Actions](https://github.com/davidf9999/gx-mcp-server/actions):
- Lint: `ruff`
- Type check: `mypy`
- Test: `pytest`

To run all checks locally:
```bash
just ci
```

## Telemetry

Great Expectations sends anonymous usage data to `posthog.greatexpectations.io` by default.
Set `GX_ANALYTICS_ENABLED=false` to disable telemetry.

## Future Work & Known Limitations

- **No persistent storage:** Data is in-memory; lost on restart.
- **Optional basic auth:** Use `--basic-auth user:pass` to require credentials.
- **No URL restrictions:** Use only in trusted environments.
- **No resource cleanup:** Large/long sessions may use significant RAM.
- **Concurrency:** Blocking/serial; no job queue or async.
- **API may change:** Expect early-breaking changes.

We are actively working on these limitations! Please [open an issue](https://github.com/davidf9999/gx-mcp-server/issues) 
if you have feedback or feature requests.

## Security

For production deployments, it is strongly recommended to run the server behind a reverse proxy (e.g., Nginx, Caddy, or a cloud load balancer) to handle TLS/HTTPS termination. This ensures that all communication between clients and the server is encrypted.

## Project Roadmap

See [ROADMAP-v2.md](ROADMAP-v2.md) for upcoming sprints and priority labels.

## License & Contributing

MIT License. See [CONTRIBUTING.md](CONTRIBUTING.md) for how to help!

## Author

David Front
- Email: dfront@gmail.com
- GitHub: [davidf9999](https://github.com/davidf9999)
- LinkedIn: [david-front](https://www.linkedin.com/in/david-front/)