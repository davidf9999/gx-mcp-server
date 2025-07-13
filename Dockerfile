FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml uv.lock* LICENSE README.md ./
RUN pip install uv
RUN uv sync
COPY . .
EXPOSE 8000
CMD ["uv", "run", "python", "-m", "gx_mcp_server", "--http"]
