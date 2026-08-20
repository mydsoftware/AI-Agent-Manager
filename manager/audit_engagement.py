from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class AuditPhase(str, Enum):
    """مراحل چرخه کاری ممیزی سایت."""

    PRE_CONTRACT = "pre_contract"
    POST_CONTRACT = "post_contract"


@dataclass(frozen=True)
class AuditEngagement:
    """قرارداد اجرایی ممیزی را از اصلاح جدا می‌کند."""

    url: str
    phase: AuditPhase = AuditPhase.PRE_CONTRACT
    accesses: frozenset[str] = field(default_factory=frozenset)

    @property
    def can_audit(self) -> bool:
        """ممیزی عمومی بدون دسترسی مدیریتی قابل انجام است."""
        return bool(self.url)

    @property
    def can_modify(self) -> bool:
        """اصلاح فقط پس از قرارداد و وجود حداقل یک دسترسی معتبر مجاز است."""
        return self.phase is AuditPhase.POST_CONTRACT and bool(self.accesses)

    def required_accesses_for(self, capability: str) -> tuple[str, ...]:
        """دسترسی لازم برای ادامه یک قابلیت را بدون درخواست Secret مشخص می‌کند."""
        mapping = {
            "wordpress": ("wordpress",),
            "repository": ("github",),
            "search_console": ("google_search_console",),
            "analytics": ("google_analytics",),
            "server": ("ssh_or_ftp",),
        }
        return mapping.get(capability, ())

    def remediation_status(self) -> str:
        if self.can_modify:
            return "مجاز برای اصلاح"
        return "فقط گزارش و پیشنهاد اصلاح؛ برای اجرا دسترسی لازم است"
