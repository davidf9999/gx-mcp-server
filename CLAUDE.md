# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Installation and Setup
```bash
pip install -e .[dev]
```

### Running the Server
```bash
uvicorn main:app --reload
```

### Testing
```bash
pytest                    # Run all tests
pytest tests/test_datasets.py     # Run specific test file
pytest tests/test_expectations.py
pytest tests/test_validation.py
```

### Code Quality
```bash
black .           # Format code
isort .           # Sort imports
pre-commit run --all-files  # Run pre-commit hooks
```

## Architecture Overview

This is a **Great Expectations MCP Server** that exposes Great Expectations functionality through the Model Context Protocol (MCP). The server provides data validation capabilities via FastMCP tools.

### Core Components

**FastMCP Integration** (`gx_mcp_server/__init__.py`):
- Main MCP server instance using FastMCP framework
- Registers tool modules and exposes HTTP app
- Entry point: `mcp.http_app()` (modern API, replaces deprecated `sse_app()`)

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

- **Handle-based Operations**: All operations use string handles to reference datasets and results
- **In-memory Storage**: Temporary storage for datasets and validation results during session
- **Great Expectations Integration**: Direct integration with GE context, suites, and checkpoints
- **Error Handling**: Graceful handling of missing datasets with dummy results
- **MCP Tool Decoration**: All exposed functions use `@mcp.tool()` decorator

### Dependencies

- **FastMCP**: MCP server framework
- **Great Expectations**: Core data validation library
- **FastAPI/Uvicorn**: Web server infrastructure
- **Pandas**: Data manipulation and CSV handling
- **Pydantic**: Data validation and schema definition