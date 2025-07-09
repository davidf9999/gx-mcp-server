# Great-Expectations MCP Server

> Expose Great Expectations data-quality checks as MCP tools for LLM agents.

[![PyPI version](https://img.shields.io/pypi/v/gx-mcp-server)](https://pypi.org/project/gx-mcp-server)
[![License](https://img.shields.io/github/license/your-org/gx-mcp-server)](LICENSE)

## Features

- **load_dataset** – load CSV data (file, URL, or inline) into memory  
- **create_suite** – bootstrap an ExpectationSuite (with optional profiling)  
- **add_expectation** – append rules to a suite  
- **run_checkpoint** – execute validations and stream results  
- **get_validation_result** – fetch detailed pass/fail summaries  

## Quickstart

```bash
# 1. Install in editable mode
pip install -e .[dev]

# 2. Run the server
uvicorn gx_mcp_server.app:app --reload

# 3. Explore the API docs
open http://localhost:8000/docs
```

## Manual Testing

1. **Example script**
   ```bash
   python examples/basic_roundtrip.py
   ```
   Expected:
   ```
   Loaded dataset handle: 3f2a1e72-...
   Created suite: demo_suite
   Add expectation success: True
   Validation ID: 7d4c3b91-...
   Validation summary: { "success": true, ... }
   ```

2. **Use curl**
   ```bash
   curl -sS -X POST http://localhost:8000/mcp/run \
     -H "Content-Type: application/json" \
     -d '{"tool":"load_dataset","args":{"source":"x,y\\n1,2","source_type":"inline"}}'
   ```

## Contributing & License

See [CONTRIBUTING.md](CONTRIBUTING.md) and [LICENSE](LICENSE).
