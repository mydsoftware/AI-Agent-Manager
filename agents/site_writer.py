from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class WriterResult:
    """نتیجه یک عملیات نوشتن روی سایت."""
    success: bool
    message: str
    changed: bool = False


class SiteWriter(ABC):
    """قرارداد مشترک برای Writerهای امن سایت."""

    @abstractmethod
    def set_canonical(self, url: str, canonical_url: str) -> WriterResult:
        """Canonical صفحه را تغییر می‌دهد."""
        raise NotImplementedError


class DryRunSiteWriter(SiteWriter):
    """Writer پیش‌فرض که هیچ تغییری اعمال نمی‌کند."""

    def set_canonical(self, url: str, canonical_url: str) -> WriterResult:
        return WriterResult(
            success=True,
            changed=False,
            message=f"Dry Run: Canonical صفحه {url} به {canonical_url} تغییر داده نشد.",
        )
