from __future__ import annotations

from dataclasses import dataclass, field

from agents.canonical_analyzer import CanonicalObservation
from agents.redirect_tracker import RedirectObservation


@dataclass(frozen=True)
class PageObservation:
    """مدل مشترک مشاهدات یک صفحه برای جلوگیری از وابستگی چرخشی."""
    url: str
    status: int
    title: str = ""
    meta_description: str = ""
    h1_count: int = 0
    image_count: int = 0
    images_without_alt: int = 0
    internal_links: list[str] = field(default_factory=list)
    security_headers: dict[str, str] = field(default_factory=dict)
    load_time_ms: int = 0
    redirect: RedirectObservation | None = None
    canonical_url: str | None = None
    canonical: CanonicalObservation | None = None
