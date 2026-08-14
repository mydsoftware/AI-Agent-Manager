from __future__ import annotations

from enum import Enum


class TaskStatus(str, Enum):
    """وضعیت‌های ممکن برای یک وظیفه."""

    PENDING = "در انتظار"
    RUNNING = "در حال اجرا"
    SUCCESS = "موفق"
    FAILED = "ناموفق"
    BLOCKED = "مسدود"
