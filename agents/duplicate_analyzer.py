from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import TYPE_CHECKING

from agents.url_identity import UrlIdentity

if TYPE_CHECKING:
    from agents.public_site_scanner import PageObservation


@dataclass(frozen=True)
class DuplicateGroup:
    """گروه URLهایی که یک هویت Canonical مشترک دارند."""
    key: str
    urls: tuple[str, ...]
    canonical_url: str | None


class DuplicateAnalyzer:
    """گروه‌بندی صفحات بر اساس URL Identity و Canonical."""

    def analyze(self, observations: list[PageObservation]) -> list[DuplicateGroup]:
        groups: dict[str, list[str]] = defaultdict(list)
        canonical_by_key: dict[str, str | None] = {}
        for item in observations:
            key = UrlIdentity.normalize(item.canonical_url or item.url)
            if key not in groups:
                canonical_by_key[key] = item.canonical_url
            normalized_url = UrlIdentity.normalize(item.url)
            if normalized_url not in groups[key]:
                groups[key].append(normalized_url)

        return [
            DuplicateGroup(key=key, urls=tuple(urls), canonical_url=canonical_by_key[key])
            for key, urls in groups.items()
            if len(urls) > 1
        ]
