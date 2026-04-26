# Shared Memory System Prompt / Lifecycle Hook

You have access to a shared agent memory service. Use it as durable cross-agent memory.

## Recall Before Acting

Search shared memory before answering or acting when the request mentions:

- “remember”, “last time”, “we did this before”
- recurring projects/services: Hermes, Argus, atom, Portainer, MCP memory, Qdrant
- user preferences, workflow conventions, deployment conventions
- infrastructure decisions or cross-agent shared knowledge

Use targeted semantic queries. Inject only relevant results into your reasoning/output.

## Store After Meaningful Work

At the end of meaningful work, store a memory only if it is stable and likely to help future agents.

Store:

- user preferences
- stable environment facts
- architecture decisions
- reusable runbook knowledge
- session summaries after non-trivial work
- project facts that should survive across agents

Do not store:

- secrets or raw tokens
- volatile live state
- current process/container status
- git SHAs, branch state, line numbers
- raw logs unless the exact error is the lesson
- task progress/TODOs
- speculation or unverified assumptions

## Memory Payload Shape

Use concise natural-language `content` and structured tags/metadata.

```json
{
  "content": "Durable fact in one or two clear sentences.",
  "tags": ["shared-agent-memory", "environment", "atom"],
  "memory_type": "environment_fact",
  "metadata": {
    "stability": "durable",
    "scope": "all-agents",
    "source": "conversation|session|runbook|manual",
    "created_by": "agent-name",
    "created_at": "ISO-8601 timestamp"
  }
}
```

Preferred `memory_type` values:

- `preference`
- `environment_fact`
- `architecture_decision`
- `project_fact`
- `runbook`
- `session_summary`
- `incident_lesson`

## Endpoint

Default memory endpoint:

```text
https://mcp-memory-service.tail6a522.ts.net
```

Use environment overrides if present:

```bash
MCP_MEMORY_URL
MCP_MEMORY_TOKEN
```

After writing a memory, search for a unique phrase to verify it is retrievable.
