from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urljoin

from agents.url_identity import UrlIdentity


@dataclass(frozen=True)
class CanonicalObservation:
    """نتیجه بررسی Canonical یک صفحه."""
    page_url: str
    canonical_url: str | None
    is_self_canonical: bool
    is_missing: bool
    is_external: bool


class CanonicalAnalyzer:
    """تحلیل Canonical و تشخیص صفحات بدون Canonical یا Canonical خارجی."""

    def analyze(self, page_url: str, canonical_href: str | None) -> CanonicalObservation:
        page = UrlIdentity.normalize(page_url)
        if not canonical_href or not canonical_href.strip():
            return CanonicalObservation(page, None, False, True, False)
        canonical = UrlIdentity.normalize(urljoin(page, canonical_href.strip()))
        page_host = page.split("/", 3)[2]
        canonical_host = canonical.split("/", 3)[2]
        return CanonicalObservation(
            page_url=page,
            canonical_url=canonical,
            is_self_canonical=UrlIdentity.equivalent(page, canonical),
            is_missing=False,
            is_external=page_host != canonical_host,
        )
