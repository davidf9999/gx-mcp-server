FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml uv.lock* LICENSE README.md ./
RUN pip install uv
RUN uv sync
RUN groupadd -r app && useradd --no-log-init -r -g app app
COPY . .
ARG WITH_DEV=false
RUN if [ "$WITH_DEV" = "true" ]; then \
        uv pip install -e ".[dev]"; \
    else \
        uv pip install -e .; \
    fi
USER app
EXPOSE 8000
CMD ["uv", "run", "python", "-m", "gx_mcp_server", "--http"]
