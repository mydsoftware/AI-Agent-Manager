"""سیاست تشخیص عملیات حساس که نیازمند تأیید کاربر هستند."""

from __future__ import annotations

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
