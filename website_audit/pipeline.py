from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse

from agents.public_site_scanner import PageObservation, PublicSiteScanner
from agents.website_audit import WebsiteAuditAgent, WebsiteAuditReport
from website_audit.report_writers import (
    _default_http_get,
    _domain_slug,
    _render_problems_file,
    _render_solutions_file,
)


@dataclass
class WebsiteAuditPipelineResult:
    """نتیجه اجرای کامل ممیزی با مسیر فایل‌های فارسی."""

    url: str
    mode: str
    access: bool
    language: str
    report: WebsiteAuditReport
    problems_path: Path
    solutions_path: Path
    pages_scanned: int
    auto_fix_attempted: bool = False
    auto_fix_message: str = ""
    message: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "mode": self.mode,
            "access": self.access,
            "language": self.language,
            "pages_scanned": self.pages_scanned,
            "findings_count": len(self.report.findings),
            "problems_file": str(self.problems_path),
            "solutions_file": str(self.solutions_path),
            "auto_fix_attempted": self.auto_fix_attempted,
            "auto_fix_message": self.auto_fix_message,
            "message": self.message,
            "report": self.report.to_dict(),
        }


class WebsiteAuditPipeline:
    """جریان استاندارد: اسکن → ممیزی → دو فایل فارسی → اصلاح مشروط به دسترسی."""

    def __init__(
        self,
        *,
        output_dir: str | Path = "reports",
        scanner_factory: Callable[[], PublicSiteScanner] | None = None,
        auditor: WebsiteAuditAgent | None = None,
        http_get: Callable[[str], Any] | None = None,
    ) -> None:
        self.output_dir = Path(output_dir)
        self.scanner_factory = scanner_factory
        self.auditor = auditor or WebsiteAuditAgent()
        self.http_get = http_get

    def run(
        self,
        url: str,
        *,
        mode: str = "pre_contract",
        access: bool = False,
        language: str = "fa",
        max_pages: int | None = None,
    ) -> WebsiteAuditPipelineResult:
        if language != "fa":
            raise ValueError("گزارش این Pipeline فقط به فارسی تولید می‌شود.")
        if not url or not url.strip():
            raise ValueError("URL سایت الزامی است.")

        scanner = self.scanner_factory() if self.scanner_factory else PublicSiteScanner(
            max_pages=max_pages,
            http_get=self.http_get or _default_http_get,
        )
        if max_pages is not None:
            scanner.max_pages = max_pages

        if mode == "pre_contract" and access:
            raise PermissionError("در حالت قبل از قرارداد، دسترسی نباید فعال باشد.")

        try:
            scanner.scan(url.strip(), max_pages=max_pages)
            pages = list(scanner.observations)
            audit_report = self.auditor.audit(
                url.strip(),
                mode="pre_contract",
                access=False,
                pages=pages,
            )
        except PermissionError:
            raise
        except Exception:
            pages = list(getattr(scanner, "observations", []) or [])
            if not pages:
                raise
            audit_report = self.auditor.audit(url.strip(), mode="pre_contract", access=False, pages=pages)

        domain = _domain_slug(url)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        problems_path = self.output_dir / f"{domain}-problems-{stamp}.md"
        solutions_path = self.output_dir / f"{domain}-solutions-{stamp}.md"

        problems_path.write_text(
            _render_problems_file(url=url, report=audit_report, pages_scanned=len(scanner.observations), mode=mode, access=access),
            encoding="utf-8",
        )
        solutions_path.write_text(
            _render_solutions_file(url=url, report=audit_report, mode=mode, access=access),
            encoding="utf-8",
        )

        auto_fix_attempted = False
        auto_fix_message = ""
        if access and mode == "post_contract":
            auto_fix_attempted = True
            auto_fix_message = (
                "دسترسی اعلام شده است؛ اصلاح خودکار فقط برای مواردی که ابزار امن Write دارند "
                "قابل اجراست. موارد بدون ابزار امن در فایل راه‌حل به‌صورت راهنمای دستی آمده‌اند."
            )
        elif not access:
            auto_fix_message = (
                "دسترسی مدیریتی فعال نیست؛ هیچ تغییری روی سایت اعمال نشد. "
                "برای اصلاح خودکار، دسترسی معتبر (مثلاً WordPress Application Password) را فعال کنید."
            )

        message = (
            f"ممیزی فارسی آماده شد. فایل مشکلات: {problems_path.name} — فایل راه‌حل‌ها: {solutions_path.name}"
        )
        return WebsiteAuditPipelineResult(
            url=url.strip(),
            mode=mode,
            access=access,
            language=language,
            report=audit_report,
            problems_path=problems_path,
            solutions_path=solutions_path,
            pages_scanned=len(scanner.observations),
            auto_fix_attempted=auto_fix_attempted,
            auto_fix_message=auto_fix_message,
            message=message,
        )
