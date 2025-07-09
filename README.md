# Great-Expectations MCP Server

This project exposes Great Expectations via Model Context Protocol (MCP).

## Tools
- load_dataset
- create_suite
- add_expectation
- run_checkpoint
- get_validation_result

## Quickstart
```bash
pip install -e .[dev]
uvicorn gx_mcp_server.app:app --reload
```
