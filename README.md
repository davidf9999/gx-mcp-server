# Great Expectations MCP Server

> Expose Great Expectations data-quality checks as MCP tools for LLM agents.

[![PyPI version](https://img.shields.io/pypi/v/gx-mcp-server)](https://pypi.org/project/gx-mcp-server)
[![License](https://img.shields.io/github/license/davidf9999/gx-mcp-server)](LICENSE)

## Features

- **load_dataset** – load CSV data (file, URL, or inline) into memory  
- **create_suite** – bootstrap an ExpectationSuite (with optional profiling)  
- **add_expectation** – append rules to a suite  
- **run_checkpoint** – execute validations and store results for later retrieval (no streaming)
- **get_validation_result** – fetch detailed pass/fail summaries  

## Quickstart

```bash
# 1. Install dependencies
uv sync
uv pip install -e .

# For development (includes testing tools and dotenv)
uv pip install -e ".[dev]"


# 2. Set up your environment
# Copy the example .env file and add your OpenAI API key (optional, for the AI example)
cp .env.example .env

# 3. Run all examples
python scripts/run_examples.py
```

## MCP Server Modes

The server supports multiple transport modes:

- **STDIO mode** (default): For AI clients like Claude Desktop
  ```bash
  uv run python -m gx_mcp_server
  ```

- **HTTP mode**: For web clients and testing
  ```bash
  uv run python -m gx_mcp_server --http
  ```

- **Inspector mode**: Development/debugging with MCP Inspector
  ```bash
  uv run python -m gx_mcp_server --inspect
  ```

## Manual Testing

1. **Start the server**
   ```bash
   uv run python -m gx_mcp_server --http
   ```

2. **Run the example script**
   ```bash
   uv run python examples/basic_roundtrip.py
   ```

   Expected:
   ```
   Loaded dataset handle: 3f2a1e72-...
   Created suite: demo_suite
   Add expectation success: True
   Validation ID: cb7f4cfa-...
   Validation summary: { "success": true, ... }
   ```

3. **Use MCP Inspector** for visual testing:
   ```bash
   # Terminal 1: Start server
   uv run python -m gx_mcp_server --http
   
   # Terminal 2: Run inspector
   npx @modelcontextprotocol/inspector
   # Connect to: http://localhost:8000/mcp/
   ```

4. **Run tests**:
   ```bash
   uv run pytest
   ```

   Note: You may see a harmless warning about Marshmallow `Number` field from Great Expectations - this is a known compatibility notice and doesn't affect functionality.

## Docker

You can also build and test the project entirely within a Docker container. The provided `Dockerfile` installs the dependencies with `uv` and exposes the server on port `8000`.

Build the image:

```bash
docker build -t gx-mcp-server .
```

Run the server:

```bash
docker run --rm -p 8000:8000 gx-mcp-server
```

Execute the test suite inside the container:

```bash
docker run --rm gx-mcp-server uv run pytest
```

## Architecture

This is a modern **MCP server** built with:

- **FastMCP**: Modern MCP server framework
- **Great Expectations**: Data validation library  
- **UV**: Fast Python package manager
- **Multiple transports**: STDIO, HTTP, Inspector modes

The server exposes Great Expectations functionality as MCP tools, allowing AI agents to perform data validation tasks through the standardized Model Context Protocol.

## Examples

See:
- [`examples/basic_roundtrip.py`](examples/basic_roundtrip.py) - Basic round trip demo
- [`examples/ai_expectation_roundtrip.py`](examples/ai_expectation_roundtrip.py) - Complete MCP workflow demo with AI agent

## AI-Assisted Expectation Suggestions

The server exposes low-level tools but does not generate rules by itself. If you
want help choosing expectations for a dataset, you can incorporate an external
LLM to analyze your columns and propose a rule. The
`ai_expectation_roundtrip.py` example shows one approach:

1. Load a DataFrame with `load_dataset`.
2. Create a suite with `create_suite`.
3. Ask an AI model (e.g. OpenAI's GPT) to suggest an expectation based on the
   column names.
4. Pass that suggestion to `add_expectation`.
5. Run `run_checkpoint` and retrieve the result with `get_validation_result`.

This pattern lets you combine automated suggestions with the standard tools the
server provides.

## Contributing & License

See [CONTRIBUTING.md](CONTRIBUTING.md) and [LICENSE](LICENSE).
