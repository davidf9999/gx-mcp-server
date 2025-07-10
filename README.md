# Great Expectations MCP Server

> Expose Great Expectations data-quality checks as MCP tools for LLM agents.

[![PyPI version](https://img.shields.io/pypi/v/gx-mcp-server)](https://pypi.org/project/gx-mcp-server)
[![License](https://img.shields.io/github/license/your-org/gx-mcp-server)](LICENSE)

## Features

- **load_dataset** – load CSV data (file, URL, or inline) into memory  
- **create_suite** – bootstrap an ExpectationSuite (with optional profiling)  
- **add_expectation** – append rules to a suite  
- **run_checkpoint** – execute validations and store results for later retrieval (no streaming)
- **get_validation_result** – fetch detailed pass/fail summaries  

## Quickstart

```bash
# 1. Install in editable mode
pip install -e .[dev]

# 2. Run the server
uvicorn main:app --reload

# 3. Explore the API docs
open http://localhost:8000/docs
```

## Manual Testing

1. **Run the example script**
   ```bash
   python examples/basic_roundtrip.py
   ```

   Expected:
   ```
   Loaded dataset handle: 3f2a1e72-...
   Created suite: demo_suite
   Add expectation success: True
   Validation ID: cb7f4cfa-...
   Validation summary: { "success": true, ... }
   ```

2. **Use `curl`** to call tools:
   ```bash
   curl -sS -X POST http://localhost:8000/mcp/run \
     -H "Content-Type: application/json" \
     -d '{"tool":"load_dataset","args":{"source":"x,y\\n1,2","source_type":"inline"}}'
   ```

## AI-Driven Example

We also provide an AI-driven workflow that uses an LLM to suggest an expectation and executes it:

```bash
# Ensure you have OPENAI_API_KEY set:
export OPENAI_API_KEY="your-key"

# Install OpenAI SDK
pip install openai

# Run the AI example
python examples/ai_expectation_roundtrip.py
```

Expected output:

```
Loaded dataset handle: 3f2a1e72-...
Created suite: ai_suite
AI proposed expectation: {"expectation_type": "...", "kwargs": {...}}
Add expectation succeeded: True
Validation ID: 7d4c3b91-...
Validation summary: { "success": true, ... }
```

## Examples

See:
- [`examples/basic_roundtrip.py`](examples/basic_roundtrip.py)
- [`examples/ai_expectation_roundtrip.py`](examples/ai_expectation_roundtrip.py)

## Contributing & License

See [CONTRIBUTING.md](CONTRIBUTING.md) and [LICENSE](LICENSE).
