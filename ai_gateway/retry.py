"""سیاست تلاش مجدد با Backoff نمایی."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable, TypeVar

from .models import AIProviderError

T = TypeVar("T")


@dataclass
class RetryPolicy:
    """تنظیمات تلاش مجدد."""

    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 30.0
    backoff_factor: float = 2.0


class RetryExecutor:
    """اجراکننده تلاش مجدد با Backoff نمایی."""

    def __init__(self, policy: RetryPolicy | None = None) -> None:
        self.policy = policy or RetryPolicy()
        self._attempt = 0
        self._last_error: Exception | None = None

    @property
    def attempt(self) -> int:
        """شماره تلاش فعلی."""
        return self._attempt

    @property
    def last_error(self) -> Exception | None:
        """آخرین خطای رخ‌داده."""
        return self._last_error

    def execute(self, operation: Callable[[], T], is_retryable: Callable[[Exception], bool] | None = None) -> T:
        """عملیات را با تلاش مجدد اجرا می‌کند."""
        self._attempt = 0
        self._last_error = None
        last_error: Exception | None = None

        for attempt in range(1, self.policy.max_attempts + 1):
            self._attempt = attempt
            try:
                return operation()
            except Exception as error:
                last_error = error
                self._last_error = error

                if attempt == self.policy.max_attempts:
                    break

                if is_retryable and not is_retryable(error):
                    break

                delay = min(
                    self.policy.base_delay * (self.policy.backoff_factor ** (attempt - 1)),
                    self.policy.max_delay,
                )
                time.sleep(delay)

        if last_error is not None:
            raise last_error
        raise RuntimeError("اجرای عملیات بدون نتیجه پایان یافت.")


def is_retryable_error(error: Exception) -> bool:
    """بررسی می‌کند آیا خطا قابل تلاش مجدد است."""
    if isinstance(error, AIProviderError):
        error_str = str(error).lower()
        # خطا‌های شبکه قابل تلاش مجدد هستند
        retryable_keywords = [
            "timeout", "timed out", "connection", "refused",
            "reset", "temporary", "rate limit", "429", "503", "502",
            "unavailable", "overloaded",
        ]
        return any(keyword in error_str for keyword in retryable_keywords)
    # خطا‌های غیرمنتظره قابل تلاش مجدد هستند
    return not isinstance(error, (ValueError, KeyError, TypeError))
