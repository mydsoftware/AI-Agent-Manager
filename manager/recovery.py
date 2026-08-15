from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, TypeVar

T = TypeVar("T")


@dataclass
class RecoveryPolicy:
    """قوانین تلاش مجدد برای خطاهای قابل بازیابی."""
    max_retries: int = 3


class RecoveryExecutor:
    """سازگارکننده عمومی برای اجرای مجدد عملیات."""

    def __init__(self, retries: int = 3) -> None:
        self.policy = RecoveryPolicy(max_retries=max(0, retries))

    def run(self, operation: Callable[[], T]) -> T:
        last_error: Exception | None = None
        for _ in range(self.policy.max_retries + 1):
            try:
                return operation()
            except Exception as error:
                last_error = error
        if last_error is not None:
            raise last_error
        raise RuntimeError("اجرای عملیات بدون نتیجه پایان یافت.")


class ErrorRecovery(RecoveryExecutor):
    """نام قدیمی API برای سازگاری با نسخه‌های قبلی."""

    def __init__(self, policy: RecoveryPolicy | None = None) -> None:
        super().__init__(policy.max_retries if policy else 3)
