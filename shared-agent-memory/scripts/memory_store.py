#!/usr/bin/env python3
"""Store a memory in the shared MCP memory service."""
import argparse
import datetime as dt
import json
import os
import ssl
import sys
import urllib.error
import urllib.request

DEFAULT_URL = "https://mcp-memory-service.tail6a522.ts.net"


def request(path: str, payload: dict) -> dict:
    base = os.environ.get("MCP_MEMORY_URL", DEFAULT_URL).rstrip("/")
    token = os.environ.get("MCP_MEMORY_TOKEN")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    ctx = ssl.create_default_context()
    if os.environ.get("MCP_MEMORY_INSECURE_TLS") == "1":
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    data = json.dumps(payload).encode()
    req = urllib.request.Request(base + path, data=data, method="POST", headers=headers)
    with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
        return json.load(resp)


def main() -> int:
    p = argparse.ArgumentParser(description="Store durable shared agent memory")
    p.add_argument("--content", required=True, help="Memory text")
    p.add_argument("--type", default="note", dest="memory_type", help="Memory type")
    p.add_argument("--tags", default="shared-agent-memory", help="Comma-separated tags")
    p.add_argument("--metadata", default="{}", help="JSON metadata object")
    p.add_argument("--conversation-id", help="Optional conversation/session id")
    p.add_argument("--client-hostname", default=os.uname().nodename if hasattr(os, "uname") else None)
    args = p.parse_args()

    try:
        metadata = json.loads(args.metadata)
    except json.JSONDecodeError as e:
        print(f"Invalid --metadata JSON: {e}", file=sys.stderr)
        return 2
    if not isinstance(metadata, dict):
        print("--metadata must be a JSON object", file=sys.stderr)
        return 2

    metadata.setdefault("created_at", dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"))
    metadata.setdefault("source", "agent")

    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    if "shared-agent-memory" not in tags:
        tags.insert(0, "shared-agent-memory")

    payload = {
        "content": args.content,
        "tags": tags,
        "memory_type": args.memory_type,
        "metadata": metadata,
        "client_hostname": args.client_hostname,
    }
    if args.conversation_id:
        payload["conversation_id"] = args.conversation_id

    try:
        print(json.dumps(request("/api/memories", payload), indent=2, sort_keys=True))
        return 0
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode(errors='replace')}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
