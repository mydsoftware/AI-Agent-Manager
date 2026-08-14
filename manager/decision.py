from __future__ import annotations

from dataclasses import dataclass

from manager.agent_governance import AgentGovernance
from manager.intention import UserIntent


@dataclass
class Decision:
    """تصمیم نهایی Manager برای اجرای یک درخواست."""

    agent: str
    reason: str
    confidence: float


class DecisionEngine:
    """انتخاب ایجنت تخصصی بر اساس نیت و وضعیت Governance."""

    def __init__(self, governance: AgentGovernance | None = None) -> None:
        self.governance = governance

    def decide(self, intent: UserIntent) -> Decision:
        """ایجنت مناسب و مجاز را برای نیت کاربر انتخاب می‌کند."""
        selected = intent.agent or "developer"
        if self.governance is not None and not self.governance.can_use(selected):
            available = self.governance.available_agents()
            if not available:
                raise RuntimeError("هیچ ایجنت فعالی برای اجرای درخواست وجود ندارد.")
            selected = available[0]
            return Decision(
                selected,
                "ایجنت پیشنهادی غیرفعال بود و Manager یک ایجنت فعال را جایگزین کرد.",
                0.4,
            )
        return Decision(
            selected,
            "ایجنت ثبت‌شده و مجاز از تحلیل نیت انتخاب شد.",
            0.9 if intent.agent else 0.5,
        )
