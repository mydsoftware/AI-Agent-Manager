"""Self-Healing Loop — SWE-agent style autonomous error detection and repair.

Inspired by SWE-agent's Agent-Computer Interface:
- Read error → Analyze → Find file → Fix → Test → Repeat
- Maximum retries with exponential backoff
- Loop detection to prevent infinite repair cycles
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class Attempt:
    """Record of a single repair attempt."""

    step: str
    error: str
    command: str = ""
    files_touched: list[str] = field(default_factory=list)
    solution: str = ""
    timestamp: float = field(default_factory=time.time)
    success: bool = False


@dataclass
class HealingResult:
    """Result of the self-healing process."""

    success: bool
    attempts: list[Attempt]
    final_output: Any = None
    error: str | None = None


class SelfHealingLoop:
    """Autonomous loop that detects errors and repairs them.

    Pattern:
        execute() → error? → analyze() → find_cause() → fix() → test() → repeat

    Loop Detection:
        If the same error signature appears 3+ times, strategy changes.
    """

    def __init__(
        self,
        max_retries: int = 5,
        backoff_base: float = 1.0,
        loop_threshold: int = 3,
    ) -> None:
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self.loop_threshold = loop_threshold
        self.attempts: list[Attempt] = []
        self._error_hashes: dict[str, int] = {}

    def run(
        self,
        execute_fn: Callable,
        analyze_fn: Callable | None = None,
        fix_fn: Callable | None = None,
        test_fn: Callable | None = None,
    ) -> HealingResult:
        """Run the self-healing loop.

        Args:
            execute_fn: The main function to execute (e.g., build, test)
            analyze_fn: Analyzes error and returns (cause, files, suggestion)
            fix_fn: Applies a fix based on analysis
            test_fn: Tests if the fix worked
        """
        for attempt_num in range(self.max_retries):
            try:
                result = execute_fn()
                # Test if available
                if test_fn:
                    test_ok = test_fn(result)
                    if not test_ok:
                        raise RuntimeError("Post-execution test failed")

                self.attempts.append(Attempt(
                    step="execute",
                    error="",
                    success=True,
                ))
                return HealingResult(
                    success=True,
                    attempts=self.attempts,
                    final_output=result,
                )

            except Exception as e:
                error_msg = str(e)
                error_hash = hashlib.md5(error_msg.encode()).hexdigest()[:12]

                # Loop detection
                self._error_hashes[error_hash] = self._error_hashes.get(error_hash, 0) + 1
                is_loop = self._error_hashes[error_hash] >= self.loop_threshold

                # Analyze
                cause = ""
                files = []
                suggestion = ""
                if analyze_fn:
                    try:
                        cause, files, suggestion = analyze_fn(e, is_loop)
                    except Exception:
                        pass

                # Fix
                if fix_fn and not is_loop:
                    try:
                        fix_fn(e, cause, files, suggestion)
                    except Exception:
                        pass

                self.attempts.append(Attempt(
                    step="repair",
                    error=error_msg,
                    files_touched=files,
                    solution=suggestion,
                    success=False,
                ))

                # Backoff
                delay = self.backoff_base * (2 ** attempt_num)
                time.sleep(min(delay, 10))

                # If loop detected, break
                if is_loop:
                    return HealingResult(
                        success=False,
                        attempts=self.attempts,
                        error=f"Loop detected: same error repeated {self._error_hashes[error_hash]} times",
                    )

        return HealingResult(
            success=False,
            attempts=self.attempts,
            error=f"Max retries ({self.max_retries}) exceeded",
        )

    def get_error_summary(self) -> dict:
        """Get summary of all errors encountered."""
        error_counts: dict[str, int] = {}
        for attempt in self.attempts:
            if attempt.error:
                short = attempt.error[:100]
                error_counts[short] = error_counts.get(short, 0) + 1
        return {
            "total_attempts": len(self.attempts),
            "successful": sum(1 for a in self.attempts if a.success),
            "error_counts": error_counts,
            "loop_detected": any(
                v >= self.loop_threshold for v in self._error_hashes.values()
            ),
        }

    def reset(self) -> None:
        self.attempts.clear()
        self._error_hashes.clear()
