from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from agents.seo_health import SeoHealthAnalyzer
from agents.seo_priority import SeoPriorityAnalyzer
from agents.site_audit_report import SiteAuditReport
from agents.public_site_scanner import PageObservation


@dataclass(frozen=True)
class SeoAction:
    """اقدام پیشنهادی برای رفع یک مشکل SEO."""
    url: str
    issue: str
    severity: str
    priority: int
    action: str


class SiteAuditActionPlanner:
    """تبدیل مشکلات SEO به فهرست اقدامات فوری و قابل اجرا."""

    _ACTIONS = {
        "پاسخ HTTP خطادار": "وضعیت HTTP و علت خطا را بررسی و صفحه/مسیر را اصلاح کنید.",
        "عنوان صفحه وجود ندارد": "برای صفحه یک عنوان یکتا، توصیفی و مرتبط تعیین کنید.",
        "Canonical وجود ندارد": "برای صفحه Canonical صحیح و ترجیحاً Self-Canonical تعیین کنید.",
        "توضیحات متا وجود ندارد": "برای صفحه Meta Description مرتبط و توصیفی اضافه کنید.",
        "H1 وجود ندارد": "یک H1 واضح و مرتبط برای محتوای اصلی صفحه اضافه کنید.",
        "بیش از یک H1 وجود دارد": "ساختار Headingها را بررسی و H1 اصلی را به یک مورد محدود کنید.",
        "تصاویر بدون Alt وجود دارد": "برای تصاویر محتوایی متن Alt توصیفی و معنادار اضافه کنید.",
        "Canonical به دامنه خارجی اشاره می‌کند": "Canonical را بررسی کنید و در صورت خطا به URL معتبر همین سایت تغییر دهید.",
    }

    def __init__(self) -> None:
        self.health = SeoHealthAnalyzer()
        self.priority = SeoPriorityAnalyzer()

    def plan(self, observations: list[PageObservation]) -> tuple[SeoAction, ...]:
        actions: list[SeoAction] = []
        for page in observations:
            health = self.health.analyze(page)
            for item in self.priority.analyze(health):
                actions.append(
                    SeoAction(
                        url=page.url,
                        issue=item.issue,
                        severity=item.severity,
                        priority=item.priority,
                        action=self._ACTIONS.get(item.issue, "مشکل را بررسی و اصلاح کنید."),
                    )
                )
        return tuple(sorted(actions, key=lambda item: (item.priority, item.url, item.issue)))

    def add_to_report(self, report: SiteAuditReport, observations: list[PageObservation]) -> SiteAuditReport:
        """گزارش را با اقدامات پیشنهادی غنی می‌کند."""
        planned = [asdict(item) for item in self.plan(observations)]
        data: dict[str, Any] = report.to_dict()
        data["seo_actions"] = planned
        return _ReportWithActions(data)


class _ReportWithActions(SiteAuditReport):
    """نمای سازگار گزارش برای نگهداری فیلدهای اقدامات پیشنهادی."""

    def __init__(self, data: dict[str, Any]) -> None:
        for key, value in data.items():
            object.__setattr__(self, key, value)

    def to_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)
