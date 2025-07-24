# Instructions for AI agents

This repository hosts the **Great Expectations MCP Server** – a modern MCP server that exposes Great Expectations data-validation capabilities.

## Architecture

**Modern MCP Server** (post-refactor):
- Pure MCP server using FastMCP framework (no FastAPI dependency)
- UV package manager with pyproject.toml
- Multiple transport modes: STDIO, HTTP, Inspector
- CLI interface: `uv run python -m gx_mcp_server`

## Development Workflow

### Setup
```bash
# Install dependencies
uv sync
```

### Testing
```bash
# Run all tests
uv run pytest

# Test end-to-end functionality with examples
python scripts/run_examples.py
```

### Code Quality
```bash
# Before committing
uv run pre-commit run --all-files
uv run pytest

# Type checking (relaxed rules for development flexibility)
uv run mypy gx_mcp_server/
```

### Server Commands

**STDIO mode** (for AI clients):
```bash
uv run python -m gx_mcp_server
```

**HTTP mode** (for testing):
```bash
uv run python -m gx_mcp_server --http
```

**Inspector mode** (development):
```bash
uv run python -m gx_mcp_server --inspect
```

## Key Files

- `gx_mcp_server/__main__.py` – CLI entry point
- `gx_mcp_server/server.py` – Server factory
- `gx_mcp_server/tools/` – MCP tool implementations
- `examples/basic_roundtrip.py` – working example
- `pyproject.toml` – UV package configuration

## Notes for Agents

- The `profiler=True` flag in `create_suite` is **deprecated** by Great Expectations 1.5+. Create empty suites and add expectations manually.
- Examples are excluded from strict type checking; relax mypy warnings accordingly.
- All datasets and validation results are ephemeral unless you switch to `--storage-backend sqlite:///path/to/db`.