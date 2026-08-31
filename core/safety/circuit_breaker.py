"""Per-task circuit breaker: CLOSED / OPEN / HALF_OPEN."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, TypeVar

logger = logging.getLogger(__name__)
T = TypeVar("T")


class CircuitState(str, Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitOpenError(RuntimeError):
    """Raised when the circuit is open and calls are rejected."""


@dataclass
class CircuitBreaker:
    name: str
    failure_threshold: int = 3
    recovery_seconds: float = 30.0
    half_open_max_calls: int = 1
    state: CircuitState = CircuitState.CLOSED
    failures: int = 0
    successes: int = 0
    opened_at: float = 0.0
    half_open_calls: int = 0
    history: list[str] = field(default_factory=list)

    def allow(self) -> bool:
        if self.state == CircuitState.CLOSED:
            return True
        if self.state == CircuitState.OPEN:
            if time.time() - self.opened_at >= self.recovery_seconds:
                self.state = CircuitState.HALF_OPEN
                self.half_open_calls = 0
                logger.info("circuit %s -> HALF_OPEN", self.name)
                return True
            return False
        return self.half_open_calls < self.half_open_max_calls

    def before_call(self) -> None:
        if not self.allow():
            raise CircuitOpenError(f"circuit open: {self.name}")
        if self.state == CircuitState.HALF_OPEN:
            self.half_open_calls += 1

    def record_success(self) -> None:
        self.successes += 1
        self.failures = 0
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            logger.info("circuit %s -> CLOSED", self.name)
        self.history.append("success")

    def record_failure(self, reason: str = "error") -> None:
        self.failures += 1
        self.history.append(reason)
        if self.failures >= self.failure_threshold or self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            self.opened_at = time.time()
            logger.warning("circuit %s -> OPEN after %s failures", self.name, self.failures)

    def call(self, fn: Callable[[], T]) -> T:
        self.before_call()
        try:
            result = fn()
        except Exception as exc:
            self.record_failure(str(exc))
            raise
        self.record_success()
        return result
