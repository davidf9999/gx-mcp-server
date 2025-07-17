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

serve: ensure_uv
    {{uv_cmd}} run python -m gx_mcp_server --http
