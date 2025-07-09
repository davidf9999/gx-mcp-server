# Contributing to gx-mcp-server

We welcome all contributions: bug fixes, enhancements, docs, and tests!

## Getting Started

1. Fork this repository and clone your fork:
   ```bash
   git clone https://github.com/your-org/gx-mcp-server.git
   cd gx-mcp-server
   ```
2. Install dependencies:
   ```bash
   pip install -e .[dev]
   ```
3. Run formatting and tests:
   ```bash
   pre-commit run --all-files
   pytest
   ```
4. Start the server:
   ```bash
   uvicorn gx_mcp_server.app:app --reload
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

- Format: `black .`
- Sort imports: `isort .`
- Lint: `ruff .`
- Type check: `mypy .`

Please follow our Code of Conduct: see [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
