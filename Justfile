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
    @if [ -z "${OPENAI_API_KEY:-}" ]; then \
        echo "ERROR: OPENAI_API_KEY is not set. It is required to run the example scripts."; \
        exit 1; \
    fi
    {{uv_cmd}} run python scripts/run_examples.py

docker-build:
    docker build -t gx-mcp-server .

docker-test:
    docker run --rm gx-mcp-server uv run pytest

release: ci run-examples
    @echo "Running release process..."
    git checkout dev
    git pull origin dev
    git checkout main
    git pull origin main
    git merge dev
    git push
    @LATEST_TAG=$(git describe --tags `git rev-list --tags --max-count=1`)
    @echo "Latest tag is $LATEST_TAG"
    @read -p "Enter the new version (e.g., v0.1.0): " NEW_VERSION; \
    if [ -z "$NEW_VERSION" ]; then \
        echo "No version entered. Aborting."; \
        exit 1; \
    fi
    git tag $NEW_VERSION
    git push origin $NEW_VERSION
    echo "Successfully created and pushed tag $NEW_VERSION"
    git checkout dev
