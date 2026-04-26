#!/usr/bin/env python3
"""Search the shared MCP memory service."""
import argparse
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


def compact(result: dict) -> None:
    print(f"query: {result.get('query')}")
    print(f"total_found: {result.get('total_found')}")
    for i, item in enumerate(result.get("results", []), 1):
        memory = item.get("memory") or item
        score = item.get("similarity") or item.get("score") or item.get("similarity_score")
        content = memory.get("content", "")
        tags = memory.get("tags") or []
        h = memory.get("content_hash") or memory.get("hash") or ""
        print(f"\n{i}. score={score} hash={h}")
        if tags:
            print("   tags=" + ",".join(tags))
        print("   " + content.replace("\n", " ")[:900])


def main() -> int:
    p = argparse.ArgumentParser(description="Search durable shared agent memory")
    p.add_argument("query")
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--threshold", type=float)
    p.add_argument("--json", action="store_true", dest="as_json")
    p.add_argument("--quality-boost", action="store_true")
    args = p.parse_args()

    payload = {"query": args.query, "n_results": args.limit, "quality_boost": args.quality_boost}
    if args.threshold is not None:
        payload["similarity_threshold"] = args.threshold

    try:
        result = request("/api/search", payload)
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode(errors='replace')}", file=sys.stderr)
        return 1

    if args.as_json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        compact(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
