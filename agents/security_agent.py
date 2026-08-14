from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class SecurityFinding:
    severity: str
    category: str
    message: str


@dataclass(frozen=True)
class SecurityResult:
    passed: bool
    findings: tuple[SecurityFinding, ...] = ()


class SecurityAgent:
    """Gate امنیتی مستقل قبل از انتشار تغییرات."""

    def scan(self, diff: str | None, dependency_report: str | None = None) -> SecurityResult:
        text = diff or ""
        findings: list[SecurityFinding] = []

        patterns = (
            (r"eval\s*\(", "high", "code-execution", "استفاده از eval شناسایی شد."),
            (r"exec\s*\(", "high", "code-execution", "استفاده از exec شناسایی شد."),
            (r"(?:password|api[_-]?key|secret)\s*=\s*['\"]", "critical", "secret", "احتمال hard-code شدن Secret شناسایی شد."),
            (r"verify\s*=\s*False", "high", "tls", "غیرفعال کردن TLS verification شناسایی شد."),
        )
        for pattern, severity, category, message in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                findings.append(SecurityFinding(severity, category, message))

        report = (dependency_report or "").lower()
        if "critical" in report and ("vulnerability" in report or "vulnerabilit" in report):
            findings.append(SecurityFinding("critical", "dependency", "وابستگی دارای آسیب‌پذیری Critical گزارش شده است."))

        passed = not any(item.severity in {"critical", "high"} for item in findings)
        return SecurityResult(passed, tuple(findings))
