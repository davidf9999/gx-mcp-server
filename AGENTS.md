# Instructions for AI agents

This repository hosts the **Great Expectations MCP Server** - a modern MCP server that exposes Great Expectations data validation capabilities.

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

# Test MCP server
uv run python -m gx_mcp_server --http  # Terminal 1
uv run python examples/basic_roundtrip.py  # Terminal 2
```

### Code Quality
```bash
# Before committing
uv run pre-commit run --all-files
uv run pytest

# Type checking (with relaxed rules for development flexibility)
uv run mypy gx_mcp_server/
```

### Linting Configuration
- **MyPy**: Relaxed rules for development flexibility
- **Examples**: Excluded from strict type checking
- **Known Warning**: Marshmallow compatibility warning from Great Expectations is harmless

### Server Commands
```bash
# STDIO mode (for AI clients)
uv run python -m gx_mcp_server

# HTTP mode (for testing)
uv run python -m gx_mcp_server --http

# Inspector mode (development)
uv run python -m gx_mcp_server --inspect
```

## Key Files

- `gx_mcp_server/__main__.py` - CLI entry point
- `gx_mcp_server/server.py` - Server factory  
- `gx_mcp_server/tools/` - MCP tool implementations
- `examples/basic_roundtrip.py` - Working example
- `pyproject.toml` - UV package configuration
