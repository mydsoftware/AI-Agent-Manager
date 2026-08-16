from __future__ import annotations

import json
import sys
from pathlib import Path

from api import execute


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python -m manager <request.json>", file=sys.stderr)
        return 2

    request_path = Path(sys.argv[1])
    if not request_path.is_file():
        print(f"Request file not found: {request_path}", file=sys.stderr)
        return 2

    payload = json.loads(request_path.read_text(encoding="utf-8"))
    request = str(payload.get("request", "")).strip()
    agent = str(payload.get("agent", "developer")).strip() or "developer"

    if not request:
        print("request is required", file=sys.stderr)
        return 2

    try:
        result = execute(request, agent)
        output = {
            "status": "completed",
            "request": request,
            "agent": agent,
            "result": result,
        }
        print(json.dumps(output, ensure_ascii=False, indent=2, default=str))
        return 0
    except Exception as exc:
        output = {
            "status": "failed",
            "request": request,
            "agent": agent,
            "error": str(exc),
        }
        print(json.dumps(output, ensure_ascii=False, indent=2, default=str))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
