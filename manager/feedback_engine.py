from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class FeedbackDecision:
    accepted: bool
    score: float
    reason: str


class FeedbackEngine:
    """ارزیابی استاندارد خروجی Agent و تصمیم‌گیری برای پذیرش یا اصلاح."""

    def __init__(self, evaluator: Callable[[Any], FeedbackDecision] | None = None) -> None:
        self.evaluator = evaluator

    def evaluate(self, result: Any) -> FeedbackDecision:
        if self.evaluator is not None:
            return self.evaluator(result)
        if result is None:
            return FeedbackDecision(False, 0.0, "خروجی خالی است")
        if isinstance(result, dict) and result.get("status") in {"error", "failed"}:
            return FeedbackDecision(False, 0.0, "اجرای Agent ناموفق بود")
        return FeedbackDecision(True, 1.0, "خروجی معتبر است")
