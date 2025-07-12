# Contributing to gx-mcp-server

We welcome all contributions: bug fixes, enhancements, docs, and tests!

## Getting Started

1. Fork this repository and clone your fork:
   ```bash
   git clone https://github.com/davidf9999/gx-mcp-server.git
   cd gx-mcp-server
   ```
2. Install dependencies:
   ```bash
   uv sync
   uv pip install -e .
   ```
3. Run formatting and tests:
   ```bash
   uv run pre-commit run --all-files
   uv run pytest
   ```
4. Start the server:
   ```bash
   uv run python -m gx_mcp_server --http
   ```

## Reporting Issues

- Search existing issues first.
- Provide steps to reproduce and expected behavior.

## Pull Requests

1. Create a branch: `git checkout -b feature/your-feature`.
2. Commit changes with clear messages.
3. Push and open a PR against `main`.
4. Ensure CI (tests, lint, type checks) passes.

## Style Guidelines

- Format and lint: `uv run ruff format . && uv run ruff check . --fix`
- Type check: `uv run mypy gx_mcp_server/`

Please follow our Code of Conduct: see [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
