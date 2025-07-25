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

- Load CSV data from file, URL, or inline (up to 1 GB, configurable)
- Load tables from Snowflake or BigQuery using URI prefixes
- Define and modify ExpectationSuites (profiler flag is **deprecated**)
- Validate data and fetch detailed results (sync or async)
- Choose **in-memory** (default) or **SQLite** storage for datasets & results
- Optional **Basic** or **Bearer** token authentication for HTTP clients
- Configure **HTTP rate limiting** per minute
- Restrict origins with `--allowed-origins`
- **Prometheus** metrics on `--metrics-port`
- **OpenTelemetry** tracing via `--trace` (OTLP exporter)
- Multiple transport modes: **STDIO**, **HTTP**, **Inspector (GUI)**

## Quickstart

```bash
just install
cp .env.example .env  # optional: add your OpenAI API key
just run-examples
```

## Usage


**Help**
```bash
uv run python -m gx_mcp_server --help
```

**STDIO mode** (default for AI clients):
```bash
uv run python -m gx_mcp_server
```

**HTTP mode** (for web / API clients):
```bash
just serve
# Add basic auth
uv run python -m gx_mcp_server --http --basic-auth user:pass
# Add rate limiting
uv run python -m gx_mcp_server --http --rate-limit 30
```

**Inspector GUI** (development):
```bash
uv run python -m gx_mcp_server --inspect
# Then in another shell:
npx @modelcontextprotocol/inspector
```

## Authentication

By default, the server runs **without any authentication enabled**. For production or secure environments, you should enable one of the supported methods below.

The server supports two authentication methods for the HTTP and Inspector modes: Basic and Bearer.

### Basic Authentication

Use a simple username and password to protect the server. You can provide credentials via command-line arguments or environment variables.

**Command-line argument:**

```bash
uv run python -m gx_mcp_server --http --basic-auth myuser:mypassword
```

**Environment variables:**

```bash
export MCP_SERVER_USER=myuser
export MCP_SERVER_PASSWORD=mypassword
uv run python -m gx_mcp_server --http
```

### Bearer Authentication

For more secure, token-based authentication, you can use bearer tokens (JWTs). This is the recommended approach for production environments.

**How it Works:** The `gx-mcp-server` acts as a *resource server* and **validates** JWTs. It does not issue them. Your AI agent (the client) must first obtain a JWT from a dedicated **Identity Provider** (like Auth0, Okta, or a custom auth service).

**Configuration:**

```bash
# Example using a public key file
uv run python -m gx_mcp_server --http \
  --bearer-public-key-file /path/to/public_key.pem \
  --bearer-issuer https://my-auth-provider.com/ \
  --bearer-audience https://my-api.com

# Example using a JWKS URL
uv run python -m gx_mcp_server --http \
  --bearer-jwks https://my-auth-provider.com/.well-known/jwks.json \
  --bearer-issuer https://my-auth-provider.com/ \
  --bearer-audience https://my-api.com
```

- `--bearer-public-key-file`: Path to the RSA public key for verifying the JWT signature.
- `--bearer-jwks`: URL of the JSON Web Key Set (JWKS) to fetch the public key.
- `--bearer-issuer`: The expected issuer (`iss`) claim in the JWT.
- `--bearer-audience`: The expected audience (`aud`) claim in the JWT.

### Using the Remote Docker Image with an AI Agent

To use the `gx-mcp-server` with an AI agent, you can run the official Docker image and configure your agent to connect to it.

1.  **Run the Docker container with authentication:**

    ```bash
    docker run -d -p 8080:8000 \
      --name gx-mcp-server \
      -e MCP_SERVER_USER=myuser \
      -e MCP_SERVER_PASSWORD=mypassword \
      davidf9999/gx-mcp-server:latest
    ```

2.  **Configure your AI agent:**

    Set the following environment variables in your agent's environment:

    ```bash
    export MCP_SERVER_URL=http://localhost:8080
    export MCP_AUTH_TOKEN="myuser:mypassword" # For basic auth
    ```

    For bearer auth, you would provide the JWT (obtained from your Identity Provider) in the `MCP_AUTH_TOKEN` variable:

    ```bash
    export MCP_AUTH_TOKEN="<your_jwt>"
    ```

## Configuring Maximum CSV File Size

Default limit is **50 MB**. Override via environment variable:
```bash
export MCP_CSV_SIZE_LIMIT_MB=200  # 1–1024 MB allowed
just serve
```

## Warehouse Connectors

Install extras:
```bash
uv pip install -e .[snowflake]
uv pip install -e .[bigquery]
```

Use URI prefixes:
```python
load_dataset("snowflake://user:pass@account/db/schema/table?warehouse=WH")
load_dataset("bigquery://project/dataset/table")
```
`load_dataset` automatically detects these prefixes and delegates to the appropriate connector.

## Metrics and Tracing

- Prometheus metrics endpoint: `http://localhost:9090/metrics`
- OpenTelemetry: `uv run python -m gx_mcp_server --http --trace`

## Docker

Build and run the server in Docker:

```bash
# Build the production image
just docker-build

# Run the server
just docker-run
```

The server will be available at `http://localhost:8000`.

For development, you can build a development image that includes test dependencies and run tests or examples:

```bash
# Build the development image
just docker-build-dev

# Run tests
just docker-test

# Run examples (requires OPENAI_API_KEY in .env file)
just docker-run-examples
```

## Development

### Quickstart

```bash
just install
cp .env.example .env  # optional: add your OpenAI API key
just run-examples
```


## Telemetry

Great Expectations sends anonymous usage data to `posthog.greatexpectations.io` by default. Disable:
```bash
export GX_ANALYTICS_ENABLED=false
```

## Current Limitations

- Stores last 100 datasets / results only
- Concurrency is **in-process** (`asyncio`) – no external queue
- Expect API evolution while the project stabilises

## Security

- Run behind a reverse proxy (Nginx, Caddy, cloud LB) in production
- Supply `--ssl-certfile` / `--ssl-keyfile` only if the proxy cannot terminate TLS
- Anonymous sessions use UUIDv4; persistent apps should use `secrets.token_urlsafe(32)`

## Project Roadmap

See [ROADMAP-v2.md](ROADMAP-v2.md) for upcoming sprints.

## License & Contributing

MIT License – see [CONTRIBUTING.md](CONTRIBUTING.md) for how to help!

## Author

David Front – dfront@gmail.com | GitHub: [davidf9999](https://github.com/davidf9999)