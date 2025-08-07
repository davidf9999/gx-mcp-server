```mermaid
graph LR
  Agent[AI Agent] -->|MCP/HTTP| Server[gx-mcp-server]
  Server --> GE[Great Expectations]
  Server --> Data[CSV / Snowflake / BigQuery]
  Server --> Store[In-memory / SQLite]
  Server --> Auth[Basic / JWT]
  Server --> Obs[Prometheus / OTEL]
```