from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class AuditFinding:
    """یک ایراد قابل گزارش در ممیزی سایت."""

    category: str
    title: str
    severity: str
    impact: str
    evidence: str
    recommendation: str
    requires_access: bool = False
    effort: str = "متوسط"


@dataclass
class WebsiteAuditReport:
    """گزارش ساختاریافته ممیزی قبل از قرارداد."""

    url: str
    mode: str = "pre_contract"
    access: bool = False
    language: str = "fa"
    findings: list[AuditFinding] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "mode": self.mode,
            "access": self.access,
            "language": self.language,
            "findings": [asdict(item) for item in self.findings],
            "limitations": self.limitations,
        }


class WebsiteAuditAgent:
    """Agent ممیزی عمومی سایت؛ در حالت قبل از قرارداد فقط تحلیل خواندنی انجام می‌دهد."""

    ALLOWED_CATEGORIES = (
        "SEO",
        "Performance",
        "Mobile",
        "Accessibility",
        "Links",
        "Security",
        "UX/UI",
        "Content",
    )

    def audit(
        self,
        url: str,
        *,
        mode: str = "pre_contract",
        access: bool = False,
        observations: list[dict[str, Any]] | None = None,
    ) -> WebsiteAuditReport:
        """از مشاهدات خواندنی گزارش فارسی می‌سازد و در حالت قبل از قرارداد تغییری ایجاد نمی‌کند."""
        if not url.strip():
            raise ValueError("URL سایت الزامی است.")
        if mode != "pre_contract":
            raise ValueError("این Agent فعلاً فقط حالت pre_contract را پشتیبانی می‌کند.")
        if access:
            raise PermissionError("WebsiteAuditAgent قبل از قرارداد نباید دسترسی فعال داشته باشد.")

        report = WebsiteAuditReport(url=url.strip())
        for observation in observations or []:
            category = str(observation.get("category", "")).strip()
            if category not in self.ALLOWED_CATEGORIES:
                continue
            report.findings.append(
                AuditFinding(
                    category=category,
                    title=str(observation.get("title", "ایراد مشاهده‌شده")).strip(),
                    severity=str(observation.get("severity", "متوسط")).strip(),
                    impact=str(observation.get("impact", "نیازمند بررسی بیشتر")).strip(),
                    evidence=str(observation.get("evidence", "مشاهده عمومی سایت")).strip(),
                    recommendation=str(observation.get("recommendation", "نیازمند اصلاح فنی")).strip(),
                    requires_access=bool(observation.get("requires_access", False)),
                    effort=str(observation.get("effort", "متوسط")).strip(),
                )
            )

        report.limitations.extend(
            [
                "این گزارش فقط بر اساس اطلاعات عمومی و قابل مشاهده سایت تهیه شده است.",
                "بدون دسترسی مدیریتی، سرور یا کد منبع، برخی ایرادات قطعی قابل تأیید نیستند.",
                "هیچ فایل، محتوا، تنظیمات یا داده‌ای در سایت مشتری تغییر داده نشده است.",
            ]
        )
        return report
