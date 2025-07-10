# Instructions for AI agents

This repository hosts the **Great Expectations MCP Server**.

## Workflow
- Install dependencies with `pip install -e .[dev]` if not already installed.
- Before committing any changes, run:
  ```bash
  pre-commit run --all-files
  pytest
  ```
- Add tests for new features or bug fixes.
- Follow the style guidelines in [CONTRIBUTING.md](CONTRIBUTING.md).
