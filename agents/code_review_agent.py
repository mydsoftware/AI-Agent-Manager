from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReviewFinding:
    severity: str
    category: str
    message: str


@dataclass(frozen=True)
class ReviewResult:
    approved: bool
    findings: tuple[ReviewFinding, ...] = ()


class CodeReviewAgent:
    """بررسی اولیه تغییرات قبل از ساخت PR."""

    def review(self, diff: str | None, tests_passed: bool = True) -> ReviewResult:
        text = diff or ""
        findings: list[ReviewFinding] = []

        if not tests_passed:
            findings.append(ReviewFinding("high", "tests", "تست‌ها موفق نشده‌اند."))
        if "eval(" in text or "exec(" in text:
            findings.append(ReviewFinding("high", "security", "استفاده بالقوه ناامن از eval/exec شناسایی شد."))
        if "TODO: SECURITY" in text:
            findings.append(ReviewFinding("medium", "security", "بررسی امنیتی ناقص علامت‌گذاری شده است."))
        if "password =" in text.lower() or "api_key =" in text.lower():
            findings.append(ReviewFinding("high", "secrets", "احتمال hard-code شدن Secret شناسایی شد."))

        approved = not any(item.severity == "high" for item in findings)
        return ReviewResult(approved, tuple(findings))
