# Great Expectations MCP Server

> Expose Great Expectations data-quality checks as MCP tools for LLM agents.

[![PyPI version](https://img.shields.io/pypi/v/gx-mcp-server)](https://pypi.org/project/gx-mcp-server) 
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/gx-mcp-server)](https://pypi.org/project/gx-mcp-server) 
[![Docker Hub](https://img.shields.io/docker/pulls/davidf9999/gx-mcp-server.svg)](https://hub.docker.com/r/davidf9999/gx-mcp-server) 
[![License](https://img.shields.io/github/license/davidf9999/gx-mcp-server)](LICENSE) 
[![CI](https://github.com/davidf9999/gx-mcp-server/actions/workflows/ci.yaml/badge.svg?branch=dev)](https://github.com/davidf9999/gx-mcp-server/actions/workflows/ci.yaml) 
[![Publish](https://github.com/davidf9999/gx-mcp-server/actions/workflows/publish.yaml/badge.svg)](https://github.com/davidf9999/gx-mcp-server/actions/workflows/publish.yaml)

## Table of Contents

- [Motivation](#motivation)
- [Quick Start](#quick-start)
- [Features](#features)
- [Installation & Usage](#installation--usage)
- [MCP Client Configuration](#mcp-client-configuration)
- [Authentication](#authentication)
- [Docker](#docker)
- [Configuration](#configuration)
- [Development](#development)
- [Security](#security)
- [License & Contributing](#license--contributing)

## Motivation

Large Language Model (LLM) agents often need to interact with and validate data. Great Expectations is a powerful open-source tool for data quality, but it's not natively accessible to LLM agents. This server bridges that gap by exposing core Great Expectations functionality through the Model Context Protocol (MCP), allowing agents to:

- Programmatically load datasets from various sources.
- Define data quality rules (Expectations) on the fly.
- Run validation checks and interpret the results.
- Integrate robust data quality checks into their automated workflows.

## Quick Start

**Docker (Recommended):**
```bash
docker run -d -p 8000:8000 --name gx-mcp-server davidf9999/gx-mcp-server:latest
claude mcp add gx-mcp-server --transport http http://localhost:8000/mcp/
claude "Load CSV data id,age\n1,25\n2,19\n3,45 and validate ages 21-65, show failed records"
```

**Local Development:**
```bash
git clone https://github.com/davidf9999/gx-mcp-server && cd gx-mcp-server
just install
claude mcp add gx-mcp-server-local -- uv run python -m gx_mcp_server
```

## Installation & Usage

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

**Development Setup:**
```bash
just install                    # Install dependencies
just serve                      # Run HTTP server
just run-examples              # Try examples
just test                      # Run tests
just ci                        # Lint and type-check
```

**Server Modes:**
```bash
uv run python -m gx_mcp_server                    # STDIO (for AI clients)
uv run python -m gx_mcp_server --http             # HTTP (for web clients)
uv run python -m gx_mcp_server --inspect          # Inspector GUI
```

**With Authentication:**
```bash
uv run python -m gx_mcp_server --http --basic-auth user:pass
uv run python -m gx_mcp_server --http --rate-limit 30
```

## MCP Client Configuration

Configure any MCP-compatible client (Claude Desktop, Claude CLI, custom applications) to connect to the server.

### Claude CLI Setup

**Local Development (STDIO):**
```bash
claude mcp add gx-mcp-server-local -- uv run python -m gx_mcp_server
```

**Docker without Authentication:**
```bash
docker run -d -p 8000:8000 --name gx-mcp-server davidf9999/gx-mcp-server:latest
claude mcp add gx-mcp-server --transport http http://localhost:8000/mcp/
```

**Docker with Basic Authentication:**
```bash
docker run -d -p 8000:8000 --name gx-mcp-server \
  -e MCP_SERVER_USER=myuser -e MCP_SERVER_PASSWORD=mypass \
  davidf9999/gx-mcp-server:latest
claude mcp add gx-mcp-server --transport http \
  --header "Authorization: Basic $(echo -n 'myuser:mypass' | base64)" \
  http://localhost:8000/mcp/
```

**Remote Server with JWT:**
```bash
claude mcp add gx-mcp-server-remote --transport http \
  --header "Authorization: Bearer YOUR_JWT_TOKEN" \
  https://your-server.com:8000/mcp/
```

### Manual Configuration

For custom MCP clients, add to your config file:

**STDIO Mode:**
```json
{
  "mcpServers": {
    "gx-mcp-server": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "python", "-m", "gx_mcp_server"]
    }
  }
}
```

**HTTP Mode with Authentication:**
```json
{
  "mcpServers": {
    "gx-mcp-server": {
      "type": "http",
      "url": "https://your-server.com:8000/mcp/",
      "headers": {
        "Authorization": "Basic dXNlcjpwYXNz"
      }
    }
  }
}
```

### Testing & Management

**Test the Server:**
```bash
claude "Load CSV data id,age\n1,25\n2,19\n3,45 and validate ages 21-65, show failed records"
```

**Manage Multiple Servers:**
```bash
claude mcp add gx-local -- uv run python -m gx_mcp_server
claude mcp add gx-docker --transport http http://localhost:8000/mcp/
claude mcp list
claude mcp remove gx-local
```

### Troubleshooting

**Connection Issues:**
```bash
# Check server health (HTTP mode)
curl http://localhost:8000/mcp/health

# Check MCP server status  
claude mcp list

# Test with verbose logging
claude mcp add gx-debug -- uv run python -m gx_mcp_server --log-level DEBUG
```

**Common Issues:**
- **"Failed to connect":** Ensure server is running and port is accessible
- **"Authentication failed":** Verify credentials and auth headers are correct
- **"401 Unauthorized":** Check if server requires authentication but none provided
- **"403 Forbidden":** Authentication succeeded but insufficient permissions  
- **"File not found":** For local files, ensure paths are correct relative to server working directory
- **"Permission denied":** Check file permissions for mounted volumes in Docker

**Authentication Debugging:**
```bash
# Test server health (no auth required)
curl http://localhost:8000/mcp/health

# Test with basic auth
curl -H "Authorization: Basic $(echo -n 'user:pass' | base64)" \
     http://localhost:8000/mcp/health  

# Test with bearer token
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8000/mcp/health
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


**Legacy Environment Variables (for custom clients):**
Some clients may expect these environment variables:
```bash
export MCP_SERVER_URL=http://localhost:8000/mcp/
export MCP_AUTH_TOKEN="myuser:mypassword" # For basic auth
export MCP_AUTH_TOKEN="YOUR_JWT_TOKEN"        # For bearer auth
```

## Configuration

### CSV File Size Limit
Default: **50 MB**. Override via environment variable:
```bash
export MCP_CSV_SIZE_LIMIT_MB=200  # 1–1024 MB allowed
```

### Warehouse Connectors

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

### Metrics and Tracing
- Prometheus metrics: `http://localhost:9090/metrics`
- OpenTelemetry: `uv run python -m gx_mcp_server --http --trace`

## Docker

### Using Pre-built Images (Recommended)

The easiest way to run `gx-mcp-server` is using the official Docker image:

```bash
# Run latest stable version
docker run -d -p 8000:8000 --name gx-mcp-server davidf9999/gx-mcp-server:latest

# Run with authentication
docker run -d -p 8000:8000 --name gx-mcp-server \
  -e MCP_SERVER_USER=myuser \
  -e MCP_SERVER_PASSWORD=mypass \
  davidf9999/gx-mcp-server:latest

# Run with file access (for loading local CSV files)
docker run -d -p 8000:8000 --name gx-mcp-server \
  -v "$(pwd)/data:/app/data" \
  davidf9999/gx-mcp-server:latest
```

### Building Local Images

Build and run the server from source:

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

```bash
just install
cp .env.example .env  # optional: add your OpenAI API key
just run-examples
```

### Telemetry
Great Expectations sends anonymous usage data by default. Disable:
```bash
export GX_ANALYTICS_ENABLED=false
```

### Current Limitations
- Stores last 100 datasets/results only
- In-process asyncio concurrency (no external queue)
- API may evolve as project stabilizes

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