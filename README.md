# Shared Agent Memory Skill

Portable skill for agents that need to share durable memory through Sean's MCP memory service and optional Qdrant archive.

Install with:

```bash
npx skills add dixie-rom/agent-shared-memory-skill --all
```

Or list available skills:

```bash
npx skills add dixie-rom/agent-shared-memory-skill --list
```

Main skill:

```text
shared-agent-memory/SKILL.md
```

Included helpers:

- `shared-agent-memory/scripts/memory_store.py`
- `shared-agent-memory/scripts/memory_search.py`
- `shared-agent-memory/templates/shared-memory-system-prompt.md`

The skill intentionally stores no secrets. Configure with environment variables if needed:

```bash
export MCP_MEMORY_URL="https://mcp-memory-service.tail6a522.ts.net"
export MCP_MEMORY_TOKEN="..."   # optional, if auth is enabled later
```
