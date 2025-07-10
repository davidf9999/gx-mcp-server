# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Installation and Setup
```bash
# Install uv package manager (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project with dependencies
uv sync

# Install pre-commit hooks
uv run pre-commit install
```

### Running the Server
```bash
# STDIO mode (for AI clients like Claude Desktop)
uv run python -m gx_mcp_server

# HTTP mode (for web-based clients)  
uv run python -m gx_mcp_server --http

# Development mode with MCP Inspector (testing UI)
uv run python -m gx_mcp_server --inspect
```

### Testing
```bash
uv run pytest                         # Run all tests
uv run pytest tests/test_datasets.py  # Run specific test file
uv run pytest tests/test_expectations.py
uv run pytest tests/test_validation.py
```

### Code Quality
```bash
uv run black .                     # Format code
uv run isort .                     # Sort imports  
uv run mypy gx_mcp_server         # Type checking
uv run pre-commit run --all-files  # Run pre-commit hooks
```

### Development Workflow
```bash
# Add new dependency
uv add package-name

# Add development dependency  
uv add --dev package-name

# Update dependencies
uv sync --upgrade

# Run commands in the virtual environment
uv run python script.py
```

## Architecture Overview

This is a **Great Expectations MCP Server** that exposes Great Expectations functionality through the Model Context Protocol (MCP). The server provides data validation capabilities as MCP tools for LLM agents.

### Core Components

**MCP Server** (`gx_mcp_server/__init__.py` & `gx_mcp_server/server.py`):
- Main MCP server instance using FastMCP framework
- Supports both STDIO and HTTP transports
- Client-agnostic design works with any MCP-compatible LLM agent

**Storage Layer** (`gx_mcp_server/core/storage.py`):
- In-memory stores for DataFrames and validation results
- `DataStorage`: Manages dataset handles with UUID-based storage
- `ValidationStorage`: Stores validation results with UUID keys
- Temporary CSV file generation for Great Expectations integration

**Schema Definitions** (`gx_mcp_server/core/schema.py`):
- Pydantic models for API contracts
- Key models: `DatasetHandle`, `SuiteHandle`, `ValidationResult`, `ValidationResultDetail`

### MCP Tools

**Dataset Management** (`gx_mcp_server/tools/datasets.py`):
- `load_dataset()`: Loads CSV data from file, URL, or inline string
- Returns dataset handle for subsequent operations
- Supports three source types: "file", "url", "inline"

**Expectation Management** (`gx_mcp_server/tools/expectations.py`):
- `create_suite()`: Creates Great Expectations suite with optional profiling
- `add_expectation()`: Adds individual expectations to existing suites
- Integrates with Great Expectations context and suite management

**Validation** (`gx_mcp_server/tools/validation.py`):
- `run_checkpoint()`: Executes validation checkpoints against datasets
- `get_validation_result()`: Retrieves detailed validation results
- Handles dummy datasets gracefully for testing scenarios

### Key Design Patterns

- **Client Agnostic**: Works with any MCP-compatible LLM agent (Claude, custom agents, etc.)
- **Dual Transport**: Supports both STDIO (desktop AI apps) and HTTP (web agents)
- **Handle-based Operations**: All operations use string handles to reference datasets and results
- **In-memory Storage**: Temporary storage for datasets and validation results during session
- **Great Expectations Integration**: Direct integration with GE context, suites, and checkpoints
- **Error Handling**: Graceful handling of missing datasets with dummy results
- **Standard MCP Patterns**: Uses `@mcp.tool()` decorators following FastMCP best practices

### Dependencies

- **FastMCP**: MCP server framework (part of official MCP Python SDK)
- **Great Expectations**: Core data validation library
- **Pandas**: Data manipulation and CSV handling
- **UV**: Modern Python package manager for fast dependency resolution