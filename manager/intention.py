from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class UserIntent:
    """نمایش ساختاریافته درخواست کاربر برای تصمیم‌گیری Manager."""

    goal: str
    agent: str | None = None
    steps: list[str] = field(default_factory=list)
    repository: str | None = None


class IntentParser:
    """یک تحلیل اولیه و قطعی از متن درخواست انجام می‌دهد."""

    KEYWORDS = {
        "github": "github",
        "گیتهاب": "github",
        "تست": "qa",
        "test": "qa",
        "بررسی": "research",
        "تحقیق": "research",
        "کدنویسی": "developer",
        "توسعه": "developer",
        "برنامه": "developer",
    }

    def parse(self, request: str) -> UserIntent:
        """ایجنت مناسب را از کلیدواژه‌های شناخته‌شده استخراج می‌کند."""
        text = request.strip()
        selected_agent = None
        for keyword, agent in self.KEYWORDS.items():
            if keyword in text.lower():
                selected_agent = agent
                break
        return UserIntent(goal=text, agent=selected_agent)
