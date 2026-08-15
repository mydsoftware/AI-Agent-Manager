from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class QualityDecision:
    accepted: bool
    score: float
    reason: str


class QualityGate:
    """دروازه کنترل کیفیت خروجی Agent قبل از تحویل."""

    def __init__(self, minimum_score: float = 0.8, evaluator: Callable[[Any], float] | None = None) -> None:
        self.minimum_score = minimum_score
        self.evaluator = evaluator

    def check(self, result: Any) -> QualityDecision:
        if self.evaluator:
            score = float(self.evaluator(result))
        elif result is None:
            score = 0.0
        elif isinstance(result, dict) and result.get("status") in {"failed", "error"}:
            score = 0.0
        else:
            score = 1.0
        return QualityDecision(score >= self.minimum_score, score, "کیفیت قابل قبول است" if score >= self.minimum_score else "کیفیت خروجی پایین‌تر از حد مجاز است")
