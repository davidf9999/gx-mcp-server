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
CMD ["uv", "run", "python", "-m", "gx_mcp_instant"]
