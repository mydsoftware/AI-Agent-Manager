from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, TypeVar

T = TypeVar("T")


@dataclass
class RecoveryPolicy:
    """قوانین تلاش مجدد برای خطاهای قابل بازیابی."""

    max_retries: int = 3


class ErrorRecovery:
    """اجرای دوباره یک عملیات پس از خطا تا سقف مجاز."""

    def __init__(self, policy: RecoveryPolicy | None = None) -> None:
        self.policy = policy or RecoveryPolicy()

    def run(self, operation: Callable[[], T]) -> T:
        """عملیات را اجرا می‌کند و در صورت شکست دوباره تلاش می‌کند."""
        last_error: Exception | None = None
        for _ in range(self.policy.max_retries + 1):
            try:
                return operation()
            except Exception as error:
                last_error = error
        if last_error is not None:
            raise last_error
        raise RuntimeError("اجرای عملیات بدون نتیجه پایان یافت.")
