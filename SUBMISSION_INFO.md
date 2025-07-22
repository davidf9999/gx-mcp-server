# Project Information for Registry Submissions

This document contains canonical information for submitting `gx‑mcp‑server` to existing Model Context Protocol (MCP) server registries, directories, and curated lists.

## One‑Liner Description
Exposes Great Expectations data‑quality checks as MCP tools for LLM agents.

## Short Description
`gx‑mcp‑server` is an open‑source Python server that bridges LLM agents and robust data quality. It exposes Great Expectations functionality through the Model Context Protocol (MCP), enabling any MCP‑compatible client to load datasets, define expectations, and run validation checks programmatically—empowering agents with dataset‑aware reliability in automated workflows.

---

## Key Information

- **Project Name:** `gx‑mcp‑server`
- **GitHub URL:** https://github.com/davidf9999/gx-mcp-server
- **PyPI URL:** https://pypi.org/project/gx-mcp-server/
- **Docker Hub URL:** https://hub.docker.com/r/davidf9999/gx-mcp-server
- **License:** MIT
- **Keywords / Tags:** `mcp`, `great-expectations`, `data-quality`, `data-validation`, `python`, `llm`, `agent`, `open-source`

---

## Targeted MCP Server Registries & Directories

### 🔹 modelcontextprotocol/registry
A community-driven RESTful API registry for MCP servers.
**Contribution Steps:**
1. Fork the repo.
2. Add a JSON/YAML entry with metadata.
3. Open a PR referencing this doc.

### 🔹 modelcontextprotocol/servers
The official GitHub list cataloging reference and community MCP servers.
**Contribution Steps:**
1. Fork the repo.
2. Insert `gx‑mcp‑server` in the “Python MCP servers” section.
3. Submit a PR with name, link, and description.

### 🔹 mcpservers.org (“Awesome MCP Servers”)
A searchable web directory of MCP server implementations.
**Contribution Steps:**
- Check site or repo for “Advertise”/“Submit”.
- Otherwise file a GitHub issue or contact maintainers with server details.

### 🔹 MCP.so registry
Community-driven MCP package index.
**Contribution Steps:**
- Use site “Submit” button or open GitHub-based PR.
- Provide metadata, tags, and transport methods.

### 🔹 mcp-get.com
CLI-based index of MCP servers.
**Contribution Steps:**
- Follow submission docs or open an issue to request inclusion.

### 🔹 Raycast MCP Registry
Used by Raycast & other MCP-aware tools.
**Contribution Steps:**
1. Fork Raycast’s registry repo.
2. Add an entry to `COMMUNITY_ENTRIES` in `entries.ts`.
3. PR with metadata and transport information.

---

## Submission Metadata Block

```yaml
name: gx‑mcp‑server
github_url: https://github.com/davidf9999/gx-mcp-server
pypi_url: https://pypi.org/project/gx-mcp-server/
docker_hub_url: https://hub.docker.com/r/davidf9999/gx-mcp-server
description: Exposes Great Expectations data‑quality checks via the Model Context Protocol, enabling LLM agents to load datasets, define expectations, and run validation checks programmatically.
language: Python
tags:
  - mcp
  - great-expectations
  - data-quality
  - data-validation
  - llm
transport: [stdio, http]  # adjust if needed
license: MIT
```

---

## Sample PR / Submission Message

```markdown
Subject: Add gx-mcp-server to [Registry Name]

Hello,

I’d like to propose adding **gx-mcp-server** to your registry/list under the [Python MCP servers / Community] section.

**Metadata:**
- Name: gx‑mcp‑server
- URL: https://github.com/davidf9999/gx-mcp-server
- Description: Exposes Great Expectations data-quality checks via MCP, enabling LLM agents to load datasets, define expectations, and run validation checks.
- Language: Python
- Tags: mcp, great-expectations, data-quality, validation, llm
- Transport: stdio, HTTP
- License: MIT

This integration brings robust data validation into the MCP ecosystem—valuable for agent workflows that require trustworthy dataset insights.

Thanks for your consideration!
```

---

## Summary Table

| Registry / Directory              | Contribution Method                              |
|-----------------------------------|--------------------------------------------------|
| modelcontextprotocol/registry     | Fork → add metadata → PR                         |
| modelcontextprotocol/servers      | Fork → insert under Python → PR                  |
| mcpservers.org                    | Use site or issue/contact maintainers            |
| MCP.so                            | Submit via site or GitHub PR                     |
| mcp-get.com                       | Follow docs or open issue                        |
| Raycast MCP Registry              | Fork → update `entries.ts` → PR                  |

---

Let me know which registry you’d like to start with—and I can help craft the exact PR or submission content for it!
