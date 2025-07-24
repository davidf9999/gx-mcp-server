# Task automation for gx-mcp-server

# Use bash with strict options
set shell := ["bash", "-euo", "pipefail", "-c"]

# Determine uv command (global or local .venv)
uv_cmd := `if command -v uv >/dev/null 2>&1; then echo uv; else echo .venv/bin/uv; fi`

# Ensure uv is available, installing into .venv if necessary
ensure_uv:
    if ! command -v uv >/dev/null 2>&1; then \
        python3 -m venv .venv && \
        .venv/bin/pip install uv; \
    fi

install: ensure_uv
    {{uv_cmd}} sync
    {{uv_cmd}} pip install -e .[dev]

test: ensure_uv
    {{uv_cmd}} run pytest

lint: ensure_uv
    {{uv_cmd}} run pre-commit run --all-files

check: ensure_uv
    {{uv_cmd}} run ruff check .

type-check: ensure_uv
    {{uv_cmd}} run mypy gx_mcp_server/

ci: lint check type-check test

serve: ensure_uv
    {{uv_cmd}} run python -m gx_mcp_server --http

run-examples: ensure_uv
    @if [ -f .env ]; then \
        export $(grep -v '^#' .env | xargs); \
    fi; \
    if [ -z "${OPENAI_API_KEY:-}" ]; then \
        echo "ERROR: OPENAI_API_KEY is not set. It is required to run the example scripts."; \
        exit 1; \
    fi; \
    {{uv_cmd}} run python scripts/run_examples.py

docker-build:
    docker build -t gx-mcp-server .

docker-build-dev:
    docker build --build-arg WITH_DEV=true -t gx-mcp-server:dev .

docker-run:
    docker run --rm -it -p 8000:8000 gx-mcp-server

docker-test:
    docker run --rm gx-mcp-server:dev uv run pytest

docker-run-examples:
    docker run --rm -e OPENAI_API_KEY --env-file .env gx-mcp-server:dev uv run python scripts/run_examples.py

docker-all: docker-build-dev docker-test docker-run-examples

# Usage: just release patch|minor|major
release level:
    @echo "Running {{level}} release process..."
    # 1. Pre-flight checks
    just ci
    just run-examples
    just docker-all

    # 2. Merge dev to main
    git checkout main
    git pull origin main
    git merge dev

    # 3. Bump version, commit, and tag
    {{uv_cmd}} run bump-my-version bump {{level}} pyproject.toml --commit --tag

    # 4. Push everything
    git push origin main --tags

    # 5. Sync dev branch
    git checkout dev
    git rebase main
    git push origin dev
    @echo "Successfully released and pushed new version."
