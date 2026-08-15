from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from bridge.project_builder import ProjectBuilder
from runtime import ManagerRuntime


def main(path: str) -> int:
    request_path = Path(path)
    request = json.loads(request_path.read_text(encoding="utf-8"))
    user_request = str(request.get("request", "")).strip()
    repository = str(request.get("repository", "")).strip()
    if not user_request or not repository:
        raise ValueError("request و repository الزامی هستند.")

    branch = str(request.get("branch") or f"ai-agent/{request_path.stem}")
    base = str(request.get("base") or "main")

    # اجرای Orchestrator برای ثبت تصمیم و مسیر Agentها.
    ManagerRuntime().run(user_request, "developer")

    result = ProjectBuilder().build(
        repository=repository,
        request=user_request,
        branch=branch,
        base=base,
        pr_title=request.get("pr_title"),
    )

    output = {
        "status": "completed",
        "repository": result.repository,
        "branch": result.branch,
        "files": result.files,
        "pull_request": result.pull_request,
    }
    out_dir = Path("agent_results")
    out_dir.mkdir(exist_ok=True)
    (out_dir / f"{request_path.stem}.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(output, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
