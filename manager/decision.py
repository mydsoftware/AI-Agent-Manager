from __future__ import annotations

from dataclasses import dataclass

from manager.intention import UserIntent


@dataclass
class Decision:
    """تصمیم نهایی Manager برای اجرای یک درخواست."""

    agent: str
    reason: str
    confidence: float


class DecisionEngine:
    """انتخاب ایجنت تخصصی بر اساس نیت تحلیل‌شده."""

    def decide(self, intent: UserIntent) -> Decision:
        """برای نیت کاربر ایجنت مناسب را انتخاب می‌کند."""
        if intent.agent:
            return Decision(intent.agent, "ایجنت از تحلیل نیت انتخاب شد.", 0.9)
        return Decision("developer", "ایجنت پیش‌فرض برای درخواست عمومی انتخاب شد.", 0.5)
