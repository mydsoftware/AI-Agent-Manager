from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from typing import Any, TYPE_CHECKING

from agents.duplicate_analyzer import DuplicateGroup
from agents.redirect_tracker import RedirectObservation
from agents.seo_health import SeoHealth, SeoHealthAnalyzer

if TYPE_CHECKING:
    from agents.public_site_scanner import PageObservation


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
    seo_score: int
    seo_status: str
    seo_issues: int
    errors: dict[str, str]
    pages: list[dict[str, Any]]
    redirect_items: list[dict[str, Any]]
    duplicate_items: list[dict[str, Any]]
    seo_items: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


class SiteAuditReportBuilder:
    """تجمیع نتایج Scanner و SEO Health در یک گزارش قابل ذخیره و انتقال."""

    def __init__(self, seo_analyzer: SeoHealthAnalyzer | None = None) -> None:
        self.seo_analyzer = seo_analyzer or SeoHealthAnalyzer()

    def build(self, observations: list[PageObservation], failures: dict[str, str], duplicate_groups: list[DuplicateGroup], redirects: list[RedirectObservation]) -> SiteAuditReport:
        missing = sum(1 for item in observations if item.canonical and item.canonical.is_missing)
        external = sum(1 for item in observations if item.canonical and item.canonical.is_external)
        duplicate_urls = sum(len(group.urls) for group in duplicate_groups)
        seo_results: list[SeoHealth] = [self.seo_analyzer.analyze(item) for item in observations]
        seo_score = round(sum(item.score for item in seo_results) / len(seo_results)) if seo_results else 0
        seo_status = "عالی" if seo_score >= 90 else "خوب" if seo_score >= 75 else "نیازمند بهبود" if seo_score >= 50 else "ضعیف"
        return SiteAuditReport(pages_scanned=len(observations), pages_failed=len(failures), redirects=len(redirects), missing_canonical=missing, external_canonical=external, duplicate_groups=len(duplicate_groups), duplicate_urls=duplicate_urls, seo_score=seo_score, seo_status=seo_status, seo_issues=sum(len(item.issues) for item in seo_results), errors=dict(failures), pages=[asdict(item) for item in observations], redirect_items=[asdict(item) for item in redirects], duplicate_items=[asdict(item) for item in duplicate_groups], seo_items=[{"url": page.url, **asdict(result)} for page, result in zip(observations, seo_results)])
