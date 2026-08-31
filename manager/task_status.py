"""وضعیت‌های استاندارد وظایف."""

from __future__ import annotations

from enum import Enum


class TaskStatus(str, Enum):
    """وضعیت‌های ممکن برای یک وظیفه."""

    # وضعیت‌های اولیه
    CREATED = "created"
    PENDING = "pending"
    PLANNING = "planning"

    # وضعیت‌های اجرایی
    ANALYZING = "analyzing"
    RUNNING = "running"
    EXECUTING = "executing"
    TESTING = "testing"
    REVIEWING = "reviewing"

    # وضعیت‌های اصلاحی
    FIXING = "fixing"
    RETRYING = "retrying"

    # وضعیت‌های تعاملی
    COMMITTING = "committing"
    CI = "ci"
    DEPLOYING = "deploying"
    VERIFYING = "verifying"

    # وضعیت‌های نهایی
    SUCCESS = "success"
    FAILED = "failed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"

    # سازگاری با نسخه قبلی (فارسی)
    در_انتظار = "pending"
    در_حال_اجرا = "running"
    موفق = "success"
    ناموفق = "failed"
    مسدود = "blocked"

    @classmethod
    def is_terminal(cls, status: "TaskStatus") -> bool:
        """بررسی می‌کند آیا وضعیت نهایی است."""
        return status in {cls.SUCCESS, cls.FAILED, cls.CANCELLED, cls.SKIPPED}

    @classmethod
    def is_retryable(cls, status: "TaskStatus") -> bool:
        """بررسی می‌کند آیا وضعیت قابل تلاش مجدد است."""
        return status in {cls.FAILED, cls.FIXING}
