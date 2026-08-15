from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ReleaseGateResult:
    ready: bool
    checks: dict[str, bool]


class ReleaseGate:
    def evaluate(self, *, tests: bool, quality: bool, security: bool, health: bool) -> ReleaseGateResult:
        checks = {"tests": tests, "quality": quality, "security": security, "health": health}
        return ReleaseGateResult(all(checks.values()), checks)
