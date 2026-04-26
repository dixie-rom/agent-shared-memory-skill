# Shared Memory Standing Instruction

Use shared memory as a durability layer, not as a reflex.

## Tool Use

If native MCP-memory tools are available, use them for recall/store/delete/update actions. Use the shared-agent-memory skill as the policy for deciding when and what to recall/store. Use this skill's helper scripts only when native MCP-memory tools are unavailable. Use Qdrant directly only for bulk RAG/document/session retrieval or ingestion, not for routine small memory writes.

## Recall

Search shared memory only when the current task depends on durable context that is likely to exist outside this prompt, such as:

- Sean’s stated preferences or recurring corrections
- prior architectural or product decisions
- stable environment conventions needed to avoid mistakes
- a past fix, incident, or runbook the user is referring to
- cross-agent context explicitly mentioned by the user

Do **not** search memory just because a familiar project or service name appears. If live state, source code, git history, or current configuration can answer better, inspect that directly.

Use the narrowest useful query. Prefer one targeted lookup over broad fishing.

## Store

Store a memory only when it is stable, reusable, and would prevent future re-discovery or repeated user steering.

Good candidates:

- explicit user preferences and corrections
- durable operating conventions
- architecture decisions and their rationale
- reusable runbook lessons after non-trivial work
- concise session summaries after meaningful completed work

Do **not** store:

- secrets or credential values
- volatile state: current status, running containers, ports, branches, SHAs, timestamps
- code line numbers or implementation details likely to drift
- raw logs or tool output unless the exact error pattern is the lesson
- ordinary task progress or TODOs
- guesses, plans, or unverified claims

## Shape

Keep `content` short and human-readable. Use tags and metadata for routing.

```json
{
  "content": "Durable fact in one or two sentences.",
  "tags": ["shared-agent-memory", "preference|environment|decision|runbook", "domain"],
  "memory_type": "preference|environment_fact|architecture_decision|project_fact|runbook|session_summary|incident_lesson",
  "metadata": {
    "stability": "durable",
    "scope": "all-agents|project|host",
    "source": "conversation|session|runbook|manual",
    "created_by": "agent-name",
    "created_at": "ISO-8601 timestamp"
  }
}
```

## Verify

After writing, search for a distinctive phrase from the memory. If it cannot be retrieved, treat the write as failed.

Default endpoint:

```text
https://mcp-memory-service.tail6a522.ts.net
```

Environment overrides:

```bash
MCP_MEMORY_URL
MCP_MEMORY_TOKEN
```
