# Project Information for Registry Submissions

## One-Liner Description
Exposes Great Expectations data-quality checks as MCP tools for LLM agents.

## Short Description
`gx-mcp-server` is an open-source Python server (≥3.11) that bridges LLM agents and robust data quality. It exposes Great Expectations functionality through the Model Context Protocol (MCP), enabling any MCP-compatible client to load datasets, define expectations, and run validation checks programmatically.

## Canonical Metadata

```yaml
name: gx-mcp-server
github_url: https://github.com/davidf9999/gx-mcp-server
pypi_url: https://pypi.org/project/gx-mcp-server/
docker_hub_url: https://hub.docker.com/r/davidf9999/gx-mcp-server
description: Exposes Great Expectations data-quality checks via MCP, enabling LLM agents to load datasets, define expectations, and run validation checks.
language: Python
requires_python: '>=3.11'
tags:
  - mcp
  - great-expectations
  - data-quality
  - data-validation
  - llm
transport: [stdio, http]
license: MIT
```

## Submission Instructions

- **modelcontextprotocol/registry** – fork & add JSON metadata
- **modelcontextprotocol/servers** – fork & add under Python list
- **mcpservers.org** – open issue or contact maintainers
- **MCP.so** – use site submit button
- **mcp-get.com** – follow docs or open issue
- **Raycast MCP Registry** – fork, add entry in `entries.ts`, open PR