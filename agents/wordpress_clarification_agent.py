from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class WordPressClarificationResult:
    needs_clarification: bool
    question: str | None
    reason: str | None


class WordPressClarificationAgent:
    """Preflight gate: asks only when a request is genuinely ambiguous for safe execution."""

    def analyze(self, request: str) -> WordPressClarificationResult:
        text = request.strip()
        if not text:
            return WordPressClarificationResult(True, "لطفاً توضیح بدهید چه پروژه‌ای می‌خواهید بسازم؟", "empty-request")

        lower = text.lower()
        has_domain = bool(re.search(r"سایت|وب.?سایت|فروشگاه|پنل|افزونه|قالب|wordpress|wordpress|website|shop|plugin|theme", lower))
        has_purpose = bool(re.search(r"برای|جهت|در زمینه|خدمات|فروش|معرفی|رزرو|آموزش|شرکت|فروشگاه|خدمات", lower))

        if len(text.split()) <= 3 and not has_purpose:
            return WordPressClarificationResult(
                True,
                "این پروژه دقیقاً برای چه هدف یا کسب‌وکاری است و چه نوع خروجی می‌خواهید؟",
                "insufficient-purpose",
            )

        if has_domain and not has_purpose and len(text.split()) <= 6:
            return WordPressClarificationResult(
                True,
                "برای اجرای خودکار، موضوع/هدف اصلی پروژه را مشخص می‌کنید؟ مثلاً معرفی شرکت، فروشگاه، خدمات یا رزرو.",
                "missing-purpose",
            )

        return WordPressClarificationResult(False, None, None)
