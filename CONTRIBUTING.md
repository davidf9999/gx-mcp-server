# Contributing to gx-mcp-server

Thank you for your interest in improving gx-mcp-server! We welcome all contributions: code, docs, tests, and feedback.

## Getting Started

1. **Fork** the repository and **clone** your fork.
2. **Install** dependencies in editable mode:
   ```bash
   pip install -e .[dev]
   ```
3. **Run tests** and format code:
   ```bash
   pytest
   pre-commit run --all-files
   ```
4. **Start the server** to test manually:
   ```bash
   uvicorn gx_mcp_server.app:app --reload
   ```

## Reporting Issues

- Check existing [issues](https://github.com/your-org/gx-mcp-server/issues) before opening.
- Create a clear, concise issue with steps to reproduce or expected behavior.

## Making Changes

1. Create a **feature branch**: `git checkout -b feature/awesome`.
2. Make small, focused commits with descriptive messages.
3. Run tests and formatting locally.
4. Push and open a **Pull Request** against `main`.
5. Reference related issues and include screenshots or logs if helpful.

## Code Style

- **Formatting**: `black .`
- **Import sorting**: `isort .`
- **Linting**: `ruff .`
- **Type checking**: `mypy .`

We follow the [Contributor Covenant v2.1](https://www.contributor-covenant.org/) – please be respectful and inclusive.
