FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
RUN groupadd -r app && useradd --no-log-init -r -m -g app app
RUN pip install uv
COPY pyproject.toml uv.lock* LICENSE README.md ./
RUN chown -R app:app /app
USER app
RUN uv sync
COPY --chown=app:app . .
ARG WITH_DEV=false
RUN if [ "$WITH_DEV" = "true" ]; then         uv pip install -e ".[dev]";     else         uv pip install -e .;     fi
EXPOSE 8000

# Set default mode to stdio, but allow override
ENV MCP_MODE=stdio

# Conditional healthcheck only for HTTP mode
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
  CMD if [ "$MCP_MODE" = "http" ]; then \
        python -c "import urllib.request, sys; urllib.request.urlopen('http://localhost:8000/mcp/health').read() or sys.exit(1)"; \
      else \
        echo "STDIO mode - no healthcheck needed"; \
      fi

# Use shell form to allow environment variable expansion
CMD if [ "$MCP_MODE" = "http" ]; then \
      uv run python -m gx_mcp_server --http --host 0.0.0.0; \
    else \
      uv run python -m gx_mcp_server; \
    fi
