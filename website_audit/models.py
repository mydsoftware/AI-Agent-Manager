from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class AccessRequest:
    """دسترسی اختیاری موردنیاز برای تحلیل عمیق‌تر را به زبان فارسی توضیح می‌دهد."""

    service: str
    title: str
    reason: str
    steps: list[str]
    url: str
    credential_name: str
    required: bool = False
    user_can_do_it: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AuditFinding:
    """یک مشکل یا پیشنهاد قابل اقدام در ممیزی سایت."""

    id: str
    category: str
    title: str
    severity: str
    evidence: str
    impact: str
    solution: list[str]
    auto_fix: bool
    user_action: list[str] = field(default_factory=list)
    status: str = "شناسایی شد"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AuditReport:
    """گزارش نهایی؛ همه متن‌های قابل نمایش به کاربر فارسی هستند."""

    url: str
    score: int
    summary: str
    findings: list[AuditFinding] = field(default_factory=list)
    access_requests: list[AccessRequest] = field(default_factory=list)
    next_steps: list[str] = field(default_factory=list)
    mode: str = "ممیزی عمومی"

    def to_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "score": self.score,
            "summary": self.summary,
            "findings": [item.to_dict() for item in self.findings],
            "access_requests": [item.to_dict() for item in self.access_requests],
            "next_steps": self.next_steps,
            "mode": self.mode,
        }
