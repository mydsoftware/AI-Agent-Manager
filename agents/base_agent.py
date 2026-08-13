from __future__ import annotations

from abc import ABC, abstractmethod

from manager.task import Task


class BaseAgent(ABC):
    """کلاس پایه برای تمام ایجنت‌های تخصصی."""

    name: str = "base"

    @abstractmethod
    def run(self, task: Task) -> str:
        """وظیفه دریافت‌شده را اجرا می‌کند و نتیجه را برمی‌گرداند."""
        raise NotImplementedError
