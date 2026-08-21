from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from typing import Any

from agents.duplicate_analyzer import DuplicateGroup
from agents.public_site_scanner import PageObservation
from agents.redirect_tracker import RedirectObservation


@dataclass(frozen=True)
class SiteAuditReport:
    """گزارش ساختاریافته ممیزی سایت."""
    pages_scanned: int
    pages_failed: int
    redirects: int
    missing_canonical: int
    external_canonical: int
    duplicate_groups: int
    duplicate_urls: int
    errors: dict[str, str]
    pages: list[dict[str, Any]]
    redirect_items: list[dict[str, Any]]
    duplicate_items: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


class SiteAuditReportBuilder:
    """تجمیع نتایج Scanner در یک گزارش قابل ذخیره و انتقال."""

    def build(
        self,
        observations: list[PageObservation],
        failures: dict[str, str],
        duplicate_groups: list[DuplicateGroup],
        redirects: list[RedirectObservation],
    ) -> SiteAuditReport:
        missing = sum(1 for item in observations if item.canonical and item.canonical.is_missing)
        external = sum(1 for item in observations if item.canonical and item.canonical.is_external)
        duplicate_urls = sum(len(group.urls) for group in duplicate_groups)
        return SiteAuditReport(
            pages_scanned=len(observations),
            pages_failed=len(failures),
            redirects=len(redirects),
            missing_canonical=missing,
            external_canonical=external,
            duplicate_groups=len(duplicate_groups),
            duplicate_urls=duplicate_urls,
            errors=dict(failures),
            pages=[asdict(item) for item in observations],
            redirect_items=[asdict(item) for item in redirects],
            duplicate_items=[asdict(item) for item in duplicate_groups],
        )
