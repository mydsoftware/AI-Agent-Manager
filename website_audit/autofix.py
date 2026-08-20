from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from .models import AuditFinding


@dataclass(frozen=True)
class FixPlan:
    """برنامه اصلاح قبل از اجرای هر تغییر."""

    finding_id: str
    عنوان: str
    توضیح: str
    قابل_اجرای_خودکار: bool
    نیازمند_تأیید_کاربر: bool = True
    مراحل: list[str] = field(default_factory=list)


@dataclass
class FixResult:
    """نتیجه اجرای یک اصلاح و امکان ممیزی مجدد."""

    finding_id: str
    status: str
    message: str
    قبل_از_اصلاح: dict[str, object] = field(default_factory=dict)
    بعد_از_اصلاح: dict[str, object] = field(default_factory=dict)
    نیازمند_ممیزی_مجدد: bool = True


class WebsiteAutoFixManager:
    """اجرای اصلاحات ایمن را فقط پس از تأیید صریح کاربر مدیریت می‌کند."""

    def build_plan(self, finding: AuditFinding) -> FixPlan:
        return FixPlan(
            finding_id=finding.id,
            عنوان=finding.title,
            توضیح="ابتدا شواهد و راهکار بررسی می‌شود؛ هیچ تغییری بدون تأیید کاربر اعمال نمی‌شود.",
            قابل_اجرای_خودکار=finding.auto_fix,
            مراحل=[
                "نمایش مشکل، شواهد و اثر آن به کاربر",
                "نمایش راهکار اصلاح به زبان فارسی",
                "درخواست تأیید صریح برای اجرای اصلاح",
                "ثبت نسخه قبل از تغییر یا ایجاد پشتیبان در صورت امکان",
                "اجرای محدودترین تغییر لازم",
                "اجرای آزمون پس از اصلاح",
                "ممیزی مجدد و مقایسه نتیجه قبل و بعد",
            ],
        )

    def apply(
        self,
        finding: AuditFinding,
        approved: bool,
        fixer: Callable[[], None],
        before: dict[str, object] | None = None,
    ) -> FixResult:
        if not finding.auto_fix:
            return FixResult(finding.id, "نیازمند اقدام کاربر", "این مورد برای اصلاح خودکار تأیید نشده و باید توسط کاربر یا متخصص اصلاح شود.", before or {})
        if not approved:
            return FixResult(finding.id, "در انتظار تأیید", "برای اجرای این اصلاح باید ابتدا تأیید صریح کاربر دریافت شود.", before or {})
        try:
            fixer()
        except Exception as error:
            return FixResult(finding.id, "ناموفق", f"اجرای اصلاح با خطا متوقف شد: {error}", before or {})
        return FixResult(finding.id, "اصلاح شد", "اصلاح اجرا شد؛ ممیزی مجدد برای تأیید نتیجه لازم است.", before or {})


class UserStepGuide:
    """وقتی Agent دسترسی لازم ندارد، کاربر را مرحله‌به‌مرحله راهنمایی می‌کند."""

    def build(self, service: str, url: str, steps: list[str]) -> dict[str, object]:
        return {
            "وضعیت": "نیازمند اقدام کاربر",
            "سرویس": service,
            "آدرس": url,
            "پیام": "اگر می‌خواهید خودتان انجام دهید، فقط مرحله فعلی را انجام دهید؛ پس از اعلام انجام شد، مرحله بعد نمایش داده می‌شود.",
            "مرحله_فعلی": 1,
            "مراحل": [{"شماره": i + 1, "دستور": step, "وضعیت": "در انتظار"} for i, step in enumerate(steps)],
            "هشدار": "کلید API یا رمز عبور را داخل گفت‌وگو ارسال نکنید؛ آن را فقط در محل امن اتصال سرویس ثبت کنید.",
        }
