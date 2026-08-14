from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class FailureAnalysis:
    """تحلیل ساختاریافته خطای CI برای چرخه تعمیر."""

    category: str
    summary: str
    root_cause_hint: str
    failing_tests: tuple[str, ...] = ()


class FailureAnalyzer:
    """لاگ CI را به اطلاعات قابل استفاده برای Repair تبدیل می‌کند."""

    _TEST_PATTERNS = (
        re.compile(r"(?:FAILED|ERROR)\s+([^\s:]+(?:::\w+)?(?:::\w+)?)"),
        re.compile(r"([\w./-]+\.py(?:::\w+)+).*?(?:AssertionError|Error|Exception)", re.S),
    )

    def analyze(self, log: str | None, status: str | None = None) -> FailureAnalysis:
        text = (log or "").strip()
        normalized = (status or "").lower()
        tests: list[str] = []
        for pattern in self._TEST_PATTERNS:
            for match in pattern.findall(text):
                value = match if isinstance(match, str) else match[0]
                if value not in tests:
                    tests.append(value)

        if normalized in {"success", "passed", "pass", "completed"}:
            return FailureAnalysis("none", "CI موفق بود.", "بدون خطا.", tuple(tests))

        lowered = text.lower()
        if "syntaxerror" in lowered:
            category = "syntax"
            hint = "خطای نحوی در کد یا فایل پیکربندی شناسایی شد."
        elif "importerror" in lowered or "modulenotfounderror" in lowered:
            category = "dependency"
            hint = "وابستگی یا مسیر import موردنیاز پیدا نشد."
        elif "assertionerror" in lowered or "failed" in lowered:
            category = "test"
            hint = "یک یا چند تست با رفتار مورد انتظار مطابقت ندارند."
        elif "permission" in lowered or "access denied" in lowered:
            category = "permission"
            hint = "دسترسی لازم برای اجرای عملیات وجود ندارد."
        elif "timeout" in lowered:
            category = "timeout"
            hint = "اجرای مرحله یا تست از زمان مجاز عبور کرده است."
        else:
            category = "unknown"
            hint = "علت دقیق از سیگنال‌های فعلی قابل تعیین نیست و نیاز به بررسی لاگ کامل دارد."

        summary = f"CI با وضعیت {status or 'failure'} شکست خورد."
        if tests:
            summary += f" تست‌های درگیر: {', '.join(tests[:10])}."
        return FailureAnalysis(category, summary, hint, tuple(tests))
