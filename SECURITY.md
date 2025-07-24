# Security Policy

This project processes arbitrary CSV data provided via HTTP or MCP tools. To limit resource usage:

- CSV files are capped at a configurable size (default 50 MB, max 1 GB).
- Only HTTP/HTTPS URLs are allowed for remote datasets.
- Uploaded datasets and validation results are stored **ephemeral in-memory** by default.
  Use `--storage-backend sqlite:///path/to/gx.db` to persist them.

## Production Deployment

- Place the HTTP server behind a reverse proxy (e.g., Nginx, Caddy, cloud LB) to terminate TLS/HTTPS.
- Monitor resource usage; the SQLite backend can grow unbounded if not pruned.
- Anonymous validation sessions use random UUIDv4 handles. For persistent user sessions:
  - Generate handles with `secrets.token_urlsafe(32)`
  - Compare them using `hmac.compare_digest` to prevent timing attacks.

## Reporting Vulnerabilities

Open a GitHub issue or email dfront@gmail.com