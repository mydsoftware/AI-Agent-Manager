"""سیاست تشخیص عملیات حساس و اعتبارسنجی تأییدیه‌های Workflow."""

from __future__ import annotations

import hashlib
import json

from manager.task import Task


SENSITIVE_TERMS = (
    "deploy", "production", "prod", "secret", "secrets", "credential", "token",
    "protected main", "main branch", "push", "release", "دامنه", "استقرار",
    "پروداکشن", "سکرت", "رمز", "توکن", "گیتهاب", "انتشار",
)


def sensitive_tasks(tasks: list[Task]) -> list[Task]:
    """Taskهایی را که اجرای آن‌ها اثر بیرونی یا حساس دارد برمی‌گرداند."""
    result: list[Task] = []
    for task in tasks:
        text = " ".join((task.title, task.description, task.agent)).lower()
        if task.agent.lower() in {"github", "github-project"} or any(term in text for term in SENSITIVE_TERMS):
            result.append(task)
    return result


def approval_fingerprint(project_id: str, action: str, tasks: list[Task]) -> str:
    """یک شناسه پایدار برای دقیقاً همان عملیات حساس تولید می‌کند."""
    payload = {
        "project_id": str(project_id),
        "action": str(action),
        "tasks": [
            {
                "id": str(task.id),
                "title": str(task.title),
                "description": str(task.description),
                "agent": str(task.agent),
                "depends_on": sorted(str(item) for item in task.depends_on),
            }
            for task in sorted(tasks, key=lambda item: str(item.id))
        ],
    }
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
