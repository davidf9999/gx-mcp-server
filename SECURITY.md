# Security Policy

This project processes arbitrary CSV data provided via HTTP or MCP tools. To limit resource usage:

- CSV files are capped at a configurable size (default 50 MB).
- Only HTTP/HTTPS URLs are allowed for remote datasets.
- Uploaded datasets and validation results are stored in-memory only.

For production deployments place the HTTP server behind a reverse proxy and monitor resource usage.
