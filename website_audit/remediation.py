from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable, Mapping, Sequence


@dataclass(frozen=True)
class AuditSnapshot:
    """تصویر ثابت از وضعیت ممیزی قبل یا بعد از اصلاح."""

    audit_id: str
    url: str
    created_at: str
    score: float
    finding_ids: tuple[str, ...]
    metrics: Mapping[str, float] = field(default_factory=dict)
    screenshot_path: str | None = None


@dataclass(frozen=True)
class RemediationResult:
    """نتیجه یک چرخه اصلاح و ممیزی مجدد."""

    status: str
    message: str
    before: AuditSnapshot
    after: AuditSnapshot | None
    improved: bool
    rollback_available: bool


class WebsiteRemediationManager:
    """چرخه امن اصلاح، ثبت وضعیت، ممیزی مجدد و امکان بازگشت را مدیریت می‌کند."""

    def __init__(self, audit: Callable[[str], AuditSnapshot], store: Callable[[AuditSnapshot], None]):
        self.audit = audit
        self.store = store

    @staticmethod
    def snapshot(
        audit_id: str,
        url: str,
        score: float,
        finding_ids: Sequence[str],
        metrics: Mapping[str, float] | None = None,
        screenshot_path: str | None = None,
    ) -> AuditSnapshot:
        return AuditSnapshot(
            audit_id=audit_id,
            url=url,
            created_at=datetime.now(timezone.utc).isoformat(),
            score=float(score),
            finding_ids=tuple(finding_ids),
            metrics=dict(metrics or {}),
            screenshot_path=screenshot_path,
        )

    def remediate(
        self,
        before: AuditSnapshot,
        apply_change: Callable[[], None],
        rollback: Callable[[], None] | None = None,
        screenshot_after: Callable[[], str | None] | None = None,
    ) -> RemediationResult:
        """اصلاح را اجرا می‌کند و فقط پس از ممیزی مجدد درباره نتیجه تصمیم می‌گیرد."""
        self.store(before)
        try:
            apply_change()
        except Exception as exc:
            return RemediationResult(
                status="ناموفق",
                message=f"اجرای اصلاح با خطا متوقف شد: {exc}",
                before=before,
                after=None,
                improved=False,
                rollback_available=rollback is not None,
            )

        after = self.audit(before.url)
        if screenshot_after is not None:
            after = AuditSnapshot(
                audit_id=after.audit_id,
                url=after.url,
                created_at=after.created_at,
                score=after.score,
                finding_ids=after.finding_ids,
                metrics=after.metrics,
                screenshot_path=screenshot_after(),
            )
        self.store(after)

        improved = after.score >= before.score and len(after.finding_ids) <= len(before.finding_ids)
        if not improved and rollback is not None:
            rollback()
            return RemediationResult(
                status="بازگشت",
                message="ممیزی مجدد نشان داد نتیجه اصلاح بهتر نشده است؛ تغییر برگشت داده شد.",
                before=before,
                after=after,
                improved=False,
                rollback_available=True,
            )

        return RemediationResult(
            status="موفق" if improved else "نیازمند بررسی",
            message=(
                "اصلاح باعث بهبود قابل اندازه‌گیری شد و نتیجه ثبت شد."
                if improved
                else "اصلاح اجرا شد اما بهبود قطعی مشاهده نشد؛ بررسی انسانی لازم است."
            ),
            before=before,
            after=after,
            improved=improved,
            rollback_available=rollback is not None,
        )
