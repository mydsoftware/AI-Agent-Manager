from __future__ import annotations

from dataclasses import dataclass

from agents.seo_priority import SeoPriorityItem


@dataclass(frozen=True)
class SeoActionPolicy:
    """سیاست اجرای خودکار یک اقدام SEO."""
    mode: str
    reason: str


class SeoActionPolicyAnalyzer:
    """تعیین می‌کند اقدام خودکار، نیازمند تأیید، یا صرفاً گزارشی باشد."""

    def decide(self, item: SeoPriorityItem) -> SeoActionPolicy:
        if item.issue in {"پاسخ HTTP خطادار", "Canonical به دامنه خارجی اشاره می‌کند"}:
            return SeoActionPolicy("گزارش شود", "اصلاح می‌تواند روی دسترسی یا مقصد URL اثر مستقیم داشته باشد.")
        if item.issue in {"عنوان صفحه وجود ندارد", "توضیحات متا وجود ندارد", "H1 وجود ندارد", "بیش از یک H1 وجود دارد", "تصاویر بدون Alt وجود دارد"}:
            return SeoActionPolicy("نیازمند تأیید", "پیشنهاد اصلاح مشخص است اما تغییر محتوای سایت باید قبل از اعمال تأیید شود.")
        if item.issue == "Canonical وجود ندارد":
            return SeoActionPolicy("قابل اصلاح خودکار", "می‌توان Self-Canonical را بدون تغییر محتوای اصلی صفحه پیشنهاد و اعمال کرد.")
        return SeoActionPolicy("نیازمند تأیید", "نوع اصلاح برای اجرای ایمن نیازمند بررسی است.")
