#!/usr/bin/env python3
"""
Perplexity API research script.

Usage:
    python perplexity_research.py --query "your query" [--model sonar] [--system-prompt "context"]

Models:
    sonar       - fast, good for most queries (default)
    sonar-pro   - deeper, richer, use for complex/strategic research

API key search order:
    1. PERPLEXITY_API_KEY environment variable
    2. ~/.claude/.secrets.env (KEY=value format)
    3. ./.env in the current working directory
    4. Skill-local .env at <skill>/.env
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

# Ensure UTF-8 output on Windows
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def load_api_key() -> str:
    """Read PERPLEXITY_API_KEY from env or any of the standard secret locations."""
    env_key = os.environ.get("PERPLEXITY_API_KEY", "").strip()
    if env_key and env_key != "your_key_here":
        return env_key

    home = Path(os.path.expanduser("~"))
    env_paths = [
        home / ".claude" / ".secrets.env",
        Path.cwd() / ".env",
        Path(__file__).parent.parent / ".env",
    ]

    for env_path in env_paths:
        if not env_path.exists():
            continue
        try:
            with open(env_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("PERPLEXITY_API_KEY="):
                        key = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if key and key != "your_key_here":
                            return key
        except OSError:
            continue

    print("Error: PERPLEXITY_API_KEY not found in any of:", file=sys.stderr)
    for p in env_paths:
        print(f"  - {p}", file=sys.stderr)
    print("Set the env var or add it to ~/.claude/.secrets.env", file=sys.stderr)
    sys.exit(1)


def call_perplexity(query: str, model: str, system_prompt: str, api_key: str) -> dict:
    """Call the Perplexity chat completions API."""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": query})

    payload = json.dumps({
        "model": model,
        "messages": messages,
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.perplexity.ai/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"Error: Perplexity API returned {e.code}", file=sys.stderr)
        print(f"Response: {body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Error: Could not reach Perplexity API - {e.reason}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Query the Perplexity API for deep research.")
    parser.add_argument("--query", required=True, help="The research query to send")
    parser.add_argument("--model", default="sonar", choices=["sonar", "sonar-pro"], help="Perplexity model (default: sonar)")
    parser.add_argument("--system-prompt", default="", help="Optional system prompt with context for Perplexity")
    args = parser.parse_args()

    api_key = load_api_key()
    result = call_perplexity(args.query, args.model, args.system_prompt, api_key)

    content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
    print(content)

    citations = result.get("citations", [])
    if citations:
        print("\n--- Sources ---")
        for i, citation in enumerate(citations, 1):
            print(f"[{i}] {citation}")


if __name__ == "__main__":
    main()
