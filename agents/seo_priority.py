from __future__ import annotations

from dataclasses import dataclass

from agents.seo_health import SeoHealth


@dataclass(frozen=True)
class SeoPriorityItem:
    """یک مشکل SEO همراه با شدت و اولویت اصلاح."""
    issue: str
    severity: str
    priority: int


class SeoPriorityAnalyzer:
    """تبدیل مشکلات SEO به اولویت‌های قابل اقدام."""

    _CRITICAL = {"پاسخ HTTP خطادار"}
    _HIGH = {"عنوان صفحه وجود ندارد", "Canonical وجود ندارد"}
    _MEDIUM = {"توضیحات متا وجود ندارد", "H1 وجود ندارد", "بیش از یک H1 وجود دارد"}

    def analyze(self, health: SeoHealth) -> tuple[SeoPriorityItem, ...]:
        result: list[SeoPriorityItem] = []
        for issue in health.issues:
            if issue in self._CRITICAL:
                severity, priority = "بحرانی", 1
            elif issue in self._HIGH:
                severity, priority = "زیاد", 2
            elif issue in self._MEDIUM:
                severity, priority = "متوسط", 3
            else:
                severity, priority = "کم", 4
            result.append(SeoPriorityItem(issue, severity, priority))
        return tuple(sorted(result, key=lambda item: item.priority))
