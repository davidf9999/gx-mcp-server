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
   You can also run `just install` to automatically set up `uv` in a virtual
   environment and install all dependencies.
3. Run formatting and tests:
   ```bash
   uv run pre-commit run --all-files
   uv run pytest
   ```
   Or simply run `just lint` or `just test` to execute these steps.
   Or run the tests inside Docker using the provided image:
   ```bash
   docker build -t gx-mcp-server .
   docker run --rm gx-mcp-server uv run pytest
   ```
4. Verify the setup by running the examples:
   ```bash
   uv run python scripts/run_examples.py
   ```
   Use `just serve` to start the HTTP server for local testing.

## Continuous Integration

All pull requests and pushes to `dev` are automatically checked by [GitHub Actions](https://github.com/davidf9999/gx-mcp-server/actions).
Tests, linters, and type checks will run automatically. Your pull request must pass these checks to be merged.

**Recommended before submitting a PR:**

```bash
uv sync
uv pip install -e ".[dev]"
uv run pre-commit run --all-files
uv run ruff check .
uv run mypy gx_mcp_server/
uv run pytest
```
The same workflow can be run via the Justfile with:
```bash
just install && just lint && just test
```

## Development and Release Process

The `main` branch is protected and reflects the latest published version. All new development should be done on feature branches and merged into the `dev` branch.

The release process is as follows:
1.  **Thorough Testing**: Before a release, run all tests on the `dev` branch. This includes not only the `pytest` suite but also the example scripts.
    ```bash
    just ci
    just run-examples
    ```
2.  **Run the Release Command**: Once all tests pass on `dev`, run the `release` command.
    ```bash
    just release
    ```
    This will merge `dev` into `main`, prompt for a new version tag, and push the tag to trigger the release workflow.

## Reporting Issues

- Search existing issues first.
- Provide steps to reproduce and expected behavior.

## Pull Requests

1. Create a branch: `git checkout -b feature/your-feature`.
2. Commit changes with clear messages.
3. Push and open a PR against `dev`.
4. Ensure CI (tests, lint, type checks) passes.

## Style Guidelines

- Format and lint: `uv run ruff format . && uv run ruff check . --fix`
- Type check: `uv run mypy gx_mcp_server/`

Please follow our Code of Conduct: see [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).