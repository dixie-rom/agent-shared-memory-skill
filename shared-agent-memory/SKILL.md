---
name: shared-agent-memory
description: Use the shared MCP memory service and optional Qdrant archive to recall and store durable cross-agent knowledge without polluting prompts with volatile code references or secrets.
version: 1.0.0
author: dixie-rom / Hermes
license: MIT
tags:
  - memory
  - mcp
  - rag
  - qdrant
  - agents
---

# Shared Agent Memory

Use this skill whenever an agent needs durable recall across sessions, agents, or tools.

The intended architecture:

```text
Agents -> MCP memory service -> sqlite_vec today
                         \
                          -> optional Qdrant archive/RAG store
```

Treat MCP memory as the **front door** for shared agent memory. Treat Qdrant as the **archive vault** for larger semantic retrieval: session summaries, project docs, runbooks, and RAG chunks.

## Tool/Skill Division of Labor

If the agent has both MCP-memory tools/prompts and this shared-agent-memory skill, use them for different layers:

- **MCP-memory tools** are the action interface. Use them to actually recall, store, update, or delete shared memories when available.
- **This skill** is the policy and shape guide. Use it to decide whether memory access is warranted, what belongs in memory, what must not be stored, and how to tag/metadata memories.
- **Helper scripts** in this skill are fallbacks for agents that do not have native MCP-memory tools.
- **Qdrant** is the archive/RAG substrate for larger semantic retrieval and document/session stores. Do not bypass MCP-memory for ordinary small agent memories unless the task is explicitly about Qdrant/RAG ingestion.

Operational rule:

1. Decide whether recall/store is appropriate using this skill.
2. If native MCP-memory tools exist, use those.
3. If native MCP-memory tools do not exist, use `scripts/memory_search.py` or `scripts/memory_store.py`.
4. Use Qdrant directly only for bulk RAG/doc/session retrieval or ingestion, not for routine preference/fact memory writes.

## Core Rule

Store **stable, reusable knowledge**. Do **not** store facts that are better rediscovered from live systems, code, git, or APIs.

Good memory prevents a future agent from asking Sean to repeat himself.

Bad memory becomes stale ballast. Dead weight in the stack.

## What to Store

Store these:

1. **User preferences**
   - response style
   - formatting/copy-paste preferences
   - workflow preferences
   - recurring constraints

2. **Stable environment facts**
   - durable hostnames
   - stable service locations
   - credential file paths, not credential values
   - access conventions
   - long-lived container/Portainer stack roles

3. **Architecture decisions**
   - why a service exists
   - chosen split of responsibilities
   - durable tradeoffs
   - project naming decisions

4. **Reusable runbook knowledge**
   - procedures that took effort to discover
   - gotchas that are likely to recur
   - safe operational patterns

5. **Session summaries**
   - only after meaningful work
   - include what changed, why, and how to verify
   - avoid raw logs unless the exact error matters

6. **Project facts**
   - stable product/platform names
   - long-lived deployment targets
   - durable project constraints

## What Not to Store

Do not store:

- Raw secrets, API keys, tokens, passwords, private keys
- Facts that change often: current container status, live ports, running processes, branch names, git SHAs
- Code references likely to drift: line numbers, function internals, temporary file paths
- Task progress/TODOs unless converted into a durable session summary
- Raw command output unless it is the reusable lesson
- Speculation, guesses, or unverified assumptions
- Large documents verbatim; chunk them into a doc/RAG collection instead

## Memory Shape

Use concise natural language as `content`. Put routing/filtering information into tags and metadata.

Recommended payload:

```json
{
  "content": "Sean prefers copy/paste payloads as a single message with no preface or commentary.",
  "tags": ["shared-agent-memory", "user-preference", "copy-paste", "sean"],
  "memory_type": "preference",
  "metadata": {
    "stability": "durable",
    "scope": "all-agents",
    "source": "conversation|session|manual|runbook",
    "created_by": "agent-name",
    "created_at": "2026-04-26T00:00:00Z"
  }
}
```

### Memory Types

Use one of these where possible:

- `preference`
- `environment_fact`
- `architecture_decision`
- `project_fact`
- `runbook`
- `session_summary`
- `incident_lesson`

### Required Tags

Every memory should include:

- `shared-agent-memory`
- one type-ish tag, e.g. `user-preference`, `environment`, `runbook`
- one domain tag, e.g. `atom`, `hermes`, `argus`, `portainer`, `qdrant`

## Retrieval Discipline

Search shared memory only when the task depends on durable context that is likely to exist outside the current prompt:

- Sean’s stated preferences or recurring corrections
- prior architecture/product decisions
- stable environment conventions needed to avoid mistakes
- a past fix, incident, or runbook the user is referring to
- cross-agent context explicitly mentioned by the user

Do **not** search memory just because a familiar project or service name appears. If live state, source code, git history, or current configuration can answer better, inspect that directly.

Use the narrowest useful query. Prefer one targeted lookup over broad fishing.

## Storage Discipline

Store a memory only when it is stable, reusable, and would prevent future re-discovery or repeated user steering.

Ask:

1. Will this still be true next month?
2. Would rediscovering it waste time or risk mistakes?
3. Is it more useful as a memory than as live discovery?
4. Does it avoid secrets, volatile state, and drifting implementation details?

If yes, store it. If not, leave it in the transcript or inspect the live system next time.

## MCP Memory REST API

Default shared memory URL in Sean’s environment:

```text
https://mcp-memory-service.tail6a522.ts.net
```

Override with:

```bash
export MCP_MEMORY_URL="https://mcp-memory-service.tail6a522.ts.net"
```

The service currently allows anonymous access in Sean’s tailnet deployment. If auth is enabled later, pass a bearer token:

```bash
export MCP_MEMORY_TOKEN="..."
```

### Store a Memory

```bash
python scripts/memory_store.py \
  --content "Sean prefers vertical slices of functionality over layer-by-layer buildout." \
  --type preference \
  --tags shared-agent-memory,user-preference,development-style,sean \
  --metadata '{"stability":"durable","scope":"all-agents","source":"manual"}'
```

### Search Memory

```bash
python scripts/memory_search.py "Sean copy paste preference" --limit 5
```

## Qdrant Role

Use Qdrant for larger retrieval stores, not as the first write interface for small agent memories.

Good Qdrant collections:

- `agent_memory` — replicated/archived explicit memories
- `session_memory` — session summaries
- `project_docs` — docs, repo docs, runbooks
- `ops_knowledge` — atom/Portainer/Tailscale service notes

Qdrant is best for RAG and bulk semantic search. MCP memory is best as the shared tool-facing memory interface.

## Verification

After storing a memory, search for it immediately:

```bash
python scripts/memory_search.py "unique phrase from memory" --limit 3
```

If it cannot be retrieved, do not assume it worked. Check the endpoint, auth, and payload shape.

## Portable Agent Instructions

If an agent supports lifecycle hooks or system prompts, use `templates/shared-memory-system-prompt.md` from this skill. If it only supports skills, installing this skill is enough: the skill tells the agent when and how to recall/store memory.
