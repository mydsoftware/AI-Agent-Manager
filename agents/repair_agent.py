from __future__ import annotations

from dataclasses import dataclass
from manager.failure_analyzer import FailureAnalysis


@dataclass(frozen=True)
class RepairPlan:
    """پیشنهاد قابل بررسی برای اصلاح Failure."""

    strategy: str
    reason: str
    change: dict[str, str] | None = None


class RepairAgent:
    """FailureAnalysis را به RepairPlan تبدیل می‌کند.

    این لایه عمداً کد را مستقیماً تغییر نمی‌دهد؛ اجرای تغییر به Engineering/GitHub Agent سپرده می‌شود.
    """

    def plan(self, analysis: FailureAnalysis) -> RepairPlan:
        strategies = {
            "syntax": "inspect_and_fix_syntax",
            "dependency": "inspect_dependencies_and_imports",
            "test": "inspect_failing_test_and_related_code",
            "permission": "inspect_permissions_and_workflow_configuration",
            "timeout": "inspect_timeout_and_runtime_hotspots",
            "unknown": "inspect_full_ci_log_and_context",
        }
        strategy = strategies.get(analysis.category, "inspect_full_ci_log_and_context")
        reason = analysis.root_cause_hint
        if analysis.failing_tests:
            reason += " تست‌های هدف: " + ", ".join(analysis.failing_tests[:10])
        return RepairPlan(strategy=strategy, reason=reason)

    def run(self, analysis: FailureAnalysis) -> dict[str, object]:
        plan = self.plan(analysis)
        return {
            "type": "repair_plan",
            "strategy": plan.strategy,
            "reason": plan.reason,
            "change": plan.change,
            "requires_execution": True,
        }
