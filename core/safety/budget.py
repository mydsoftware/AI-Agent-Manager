"""Token / cost / time budgets per task and a daily global cap."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class BudgetExceeded(RuntimeError):
    """Raised when a task or global budget is exhausted."""


@dataclass
class UsageReport:
    task_id: str
    tokens: int = 0
    cost_usd: float = 0.0
    elapsed_seconds: float = 0.0
    model: str = ""
    provider: str = ""
    stopped_reason: str | None = None


@dataclass
class BudgetController:
    default_token_budget: int = 50_000
    default_cost_budget_usd: float = 1.0
    default_time_budget_seconds: float = 300.0
    daily_token_budget: int = 500_000
    daily_cost_budget_usd: float = 10.0
    day_key: str = field(default_factory=lambda: time.strftime("%Y-%m-%d"))
    daily_tokens: int = 0
    daily_cost: float = 0.0
    reports: dict[str, UsageReport] = field(default_factory=dict)
    _starts: dict[str, float] = field(default_factory=dict)
    _token_caps: dict[str, int] = field(default_factory=dict)
    _cost_caps: dict[str, float] = field(default_factory=dict)
    _time_caps: dict[str, float] = field(default_factory=dict)

    def _roll_day(self) -> None:
        today = time.strftime("%Y-%m-%d")
        if today != self.day_key:
            self.day_key = today
            self.daily_tokens = 0
            self.daily_cost = 0.0

    def can_start(self, task_id: str) -> None:
        self._roll_day()
        if self.daily_tokens >= self.daily_token_budget:
            raise BudgetExceeded("daily token budget exhausted")
        if self.daily_cost >= self.daily_cost_budget_usd:
            raise BudgetExceeded("daily cost budget exhausted")
        self._starts[task_id] = time.time()
        self._token_caps[task_id] = self.default_token_budget
        self._cost_caps[task_id] = self.default_cost_budget_usd
        self._time_caps[task_id] = self.default_time_budget_seconds
        self.reports.setdefault(task_id, UsageReport(task_id=task_id))

    def record_tokens(
        self,
        task_id: str,
        tokens: int,
        cost_usd: float = 0.0,
        model: str = "",
        provider: str = "",
    ) -> None:
        self._roll_day()
        report = self.reports.setdefault(task_id, UsageReport(task_id=task_id))
        report.tokens += tokens
        report.cost_usd += cost_usd
        report.model = model or report.model
        report.provider = provider or report.provider
        self.daily_tokens += tokens
        self.daily_cost += cost_usd
        self._check(task_id)

    def _check(self, task_id: str) -> None:
        report = self.reports[task_id]
        started = self._starts.get(task_id, time.time())
        report.elapsed_seconds = time.time() - started
        if report.tokens > self._token_caps.get(task_id, self.default_token_budget):
            report.stopped_reason = "token_budget"
            raise BudgetExceeded(f"token budget exceeded for {task_id}")
        if report.cost_usd > self._cost_caps.get(task_id, self.default_cost_budget_usd):
            report.stopped_reason = "cost_budget"
            raise BudgetExceeded(f"cost budget exceeded for {task_id}")
        if report.elapsed_seconds > self._time_caps.get(task_id, self.default_time_budget_seconds):
            report.stopped_reason = "time_budget"
            raise BudgetExceeded(f"time budget exceeded for {task_id}")

    def check_time(self, task_id: str) -> None:
        self._check(task_id)

    def snapshot(self) -> dict:
        self._roll_day()
        return {
            "day": self.day_key,
            "daily_tokens": self.daily_tokens,
            "daily_cost_usd": self.daily_cost,
            "daily_token_budget": self.daily_token_budget,
            "daily_cost_budget_usd": self.daily_cost_budget_usd,
            "tasks": {k: vars(v) for k, v in self.reports.items()},
        }
