from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from agents.public_site_scanner import PageObservation


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
        return {"url": self.url, "mode": self.mode, "access": self.access, "language": self.language, "findings": [asdict(item) for item in self.findings], "limitations": self.limitations}


class WebsiteAuditAgent:
    """Agent ممیزی عمومی سایت؛ در حالت قبل از قرارداد فقط تحلیل خواندنی انجام می‌دهد."""
    ALLOWED_CATEGORIES = ("SEO", "Performance", "Mobile", "Accessibility", "Links", "Security", "UX/UI", "Content")

    def audit(self, url: str, *, mode: str = "pre_contract", access: bool = False, observations: list[dict[str, Any]] | None = None, pages: list[PageObservation] | None = None) -> WebsiteAuditReport:
        """مشاهدات خام اسکنر را به Findings استاندارد فارسی تبدیل می‌کند."""
        if not url.strip():
            raise ValueError("URL سایت الزامی است.")
        if mode != "pre_contract":
            raise ValueError("این Agent فعلاً فقط حالت pre_contract را پشتیبانی می‌کند.")
        if access:
            raise PermissionError("WebsiteAuditAgent قبل از قرارداد نباید دسترسی فعال داشته باشد.")
        report = WebsiteAuditReport(url=url.strip())
        raw = list(observations or [])
        for page in pages or []:
            raw.extend(self._findings_from_page(page))
        for observation in raw:
            category = str(observation.get("category", "")).strip()
            if category not in self.ALLOWED_CATEGORIES:
                continue
            report.findings.append(AuditFinding(category=category, title=str(observation.get("title", "ایراد مشاهده‌شده")).strip(), severity=str(observation.get("severity", "متوسط")).strip(), impact=str(observation.get("impact", "نیازمند بررسی بیشتر")).strip(), evidence=str(observation.get("evidence", "مشاهده عمومی سایت")).strip(), recommendation=str(observation.get("recommendation", "نیازمند اصلاح فنی")).strip(), requires_access=bool(observation.get("requires_access", False)), effort=str(observation.get("effort", "متوسط")).strip()))
        report.limitations.extend(["این گزارش فقط بر اساس اطلاعات عمومی و قابل مشاهده سایت تهیه شده است.", "بدون دسترسی مدیریتی، سرور یا کد منبع، برخی ایرادات قطعی قابل تأیید نیستند.", "هیچ فایل، محتوا، تنظیمات یا داده‌ای در سایت مشتری تغییر داده نشده است."])
        return report

    def _findings_from_page(self, page: PageObservation) -> list[dict[str, Any]]:
        """چند قاعده قطعی و قابل توضیح را از مشاهدات صفحه استخراج می‌کند."""
        findings: list[dict[str, Any]] = []
        if not page.title:
            findings.append({"category": "SEO", "title": "عنوان صفحه وجود ندارد", "severity": "زیاد", "impact": "کاهش کیفیت معرفی صفحه به موتورهای جستجو", "evidence": f"عنوان برای {page.url} مشاهده نشد", "recommendation": "برای صفحه یک عنوان دقیق و یکتا تعریف شود", "effort": "ساده"})
        if not page.meta_description:
            findings.append({"category": "SEO", "title": "Meta Description وجود ندارد", "severity": "متوسط", "impact": "کنترل کمتر روی توضیح صفحه در نتایج جستجو", "evidence": f"Meta Description در {page.url} مشاهده نشد", "recommendation": "توضیح متای مرتبط و یکتا اضافه شود", "effort": "ساده"})
        if page.h1_count == 0:
            findings.append({"category": "SEO", "title": "تیتر H1 مشاهده نشد", "severity": "متوسط", "impact": "ساختار معنایی صفحه ضعیف‌تر می‌شود", "evidence": f"در {page.url} هیچ H1 مشاهده نشد", "recommendation": "یک H1 توصیفی و یکتا برای محتوای اصلی قرار گیرد", "effort": "ساده"})
        if page.images_without_alt:
            findings.append({"category": "Accessibility", "title": "تصویر بدون متن جایگزین", "severity": "متوسط", "impact": "دسترسی‌پذیری برای کاربران صفحه‌خوان کاهش می‌یابد", "evidence": f"{page.images_without_alt} تصویر بدون alt در {page.url}", "recommendation": "برای تصاویر معنادار alt توصیفی اضافه شود", "effort": "ساده"})
        if page.status >= 400:
            findings.append({"category": "Links", "title": "صفحه با خطای HTTP پاسخ داد", "severity": "زیاد", "impact": "کاربر ممکن است نتواند محتوای صفحه را دریافت کند", "evidence": f"HTTP {page.status} برای {page.url}", "recommendation": "علت خطای HTTP بررسی و برطرف شود", "effort": "متوسط"})
        if page.load_time_ms > 3000:
            findings.append({"category": "Performance", "title": "زمان بارگذاری بالا", "severity": "زیاد", "impact": "تجربه کاربری و احتمالاً نرخ تبدیل ضعیف‌تر می‌شود", "evidence": f"زمان ثبت‌شده: {page.load_time_ms} میلی‌ثانیه در {page.url}", "recommendation": "منابع سنگین، تصاویر، JavaScript و کش بررسی شوند", "effort": "متوسط"})
        return findings
