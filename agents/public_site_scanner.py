from __future__ import annotations

import ipaddress
import socket
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urljoin, urlparse

from agents.canonical_analyzer import CanonicalAnalyzer, CanonicalObservation
from agents.crawl_state import CrawlState
from agents.duplicate_analyzer import DuplicateAnalyzer, DuplicateGroup
from agents.redirect_tracker import RedirectObservation, RedirectTracker
from agents.site_audit_report import SiteAuditReport, SiteAuditReportBuilder
from agents.robots_policy import RobotsPolicy
from agents.site_discovery import SiteDiscovery
from agents.url_identity import UrlIdentity


@dataclass(frozen=True)
class PageObservation:
    """مشاهدات عمومی یک صفحه بدون عملیات نوشتنی."""
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


class PublicSiteScanner:
    """Crawler کامل سایت عمومی با Queue، Sitemap، robots، Redirect، Canonical و گزارش ممیزی."""

    def __init__(self, discovery: SiteDiscovery | None = None, robots_policy: RobotsPolicy | None = None) -> None:
        self.queue: deque[str] = deque()
        self.visited: set[str] = set()
        self.observations: list[PageObservation] = []
        self.failed: dict[str, str] = {}
        self.discovery = discovery or SiteDiscovery()
        self.robots_policy = robots_policy or RobotsPolicy()
        self.redirect_tracker = RedirectTracker()
        self.canonical_analyzer = CanonicalAnalyzer()
        self.duplicate_analyzer = DuplicateAnalyzer()
        self.report_builder = SiteAuditReportBuilder()
        self.robots_discovered = False

    def validate_url(self, url: str) -> str:
        value = self.normalize_url(url)
        parsed = urlparse(value)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("URL عمومی HTTP/HTTPS معتبر نیست.")
        try:
            addresses = socket.getaddrinfo(parsed.hostname, None)
        except OSError as error:
            raise ValueError("دامنه قابل Resolve نیست.") from error
        for item in addresses:
            address = ipaddress.ip_address(item[4][0])
            if address.is_private or address.is_loopback or address.is_link_local or address.is_reserved:
                raise PermissionError("اسکن آدرس‌های داخلی یا خصوصی مجاز نیست.")
        return value

    @staticmethod
    def normalize_url(url: str) -> str:
        return UrlIdentity.normalize(url)

    def initialize(self, start_url: str) -> dict[str, list[str]]:
        """Discovery را اجرا و URLهای مجاز Sitemap را وارد Queue می‌کند."""
        root = self.validate_url(start_url)
        discovered = self.discovery.discover(root)
        self._load_robots_policy(discovered.get("robots", []))
        self.enqueue([root, *discovered.get("urls", [])])
        return discovered

    def _load_robots_policy(self, lines: list[str]) -> None:
        self.robots_policy.parse("\n".join(lines))
        self.robots_discovered = True

    def enqueue(self, urls: list[str]) -> None:
        """URLهای جدید را با هویت یکتا و قوانین robots وارد صف می‌کند."""
        queued = {UrlIdentity.normalize(item) for item in self.queue}
        visited = {UrlIdentity.normalize(item) for item in self.visited}
        for url in urls:
            normalized = UrlIdentity.normalize(url)
            if not normalized or normalized in visited or normalized in queued:
                continue
            if self.robots_discovered and not self.robots_policy.is_allowed(normalized):
                continue
            self.queue.append(normalized)
            queued.add(normalized)

    def resume(self, urls: list[str]) -> None:
        """Crawl را از URLهای ذخیره‌شده ادامه می‌دهد."""
        self.enqueue(urls)

    def save_state(self, path: str | Path) -> None:
        """وضعیت فعلی صف، صفحات و خطاها را ذخیره می‌کند."""
        CrawlState(queue=list(self.queue), visited=sorted(self.visited), failed=dict(self.failed)).save(path)

    def load_state(self, path: str | Path) -> None:
        """وضعیت ذخیره‌شده را روی Scanner بازیابی می‌کند."""
        state = CrawlState.load(path)
        self.queue = deque()
        self.visited = set(state.visited)
        self.failed = dict(state.failed)
        self.enqueue(state.queue)

    def next_url(self) -> str | None:
        """URL بعدی صف را برمی‌گرداند."""
        if not self.queue:
            return None
        url = self.queue.popleft()
        self.visited.add(url)
        return url

    def record_redirect(self, source_url: str, status: int, location: str | None) -> RedirectObservation | None:
        """Redirect صفحه را ثبت می‌کند و مقصد را برای Crawl بعدی وارد Queue می‌کند."""
        observation = self.redirect_tracker.record(source_url, status, location)
        if observation is not None:
            self.enqueue([observation.destination_url])
        return observation

    def record_observation(self, observation: PageObservation) -> None:
        """نتیجه صفحه را ثبت و لینک‌های داخلی آن را وارد صف می‌کند."""
        self.observations.append(observation)
        self.enqueue(observation.internal_links)

    def duplicate_groups(self) -> list[DuplicateGroup]:
        """گروه‌های Duplicate کشف‌شده از کل صفحات اسکن‌شده را برمی‌گرداند."""
        return self.duplicate_analyzer.analyze(self.observations)

    def generate_report(self) -> SiteAuditReport:
        """گزارش کامل ممیزی را از نتایج فعلی Scanner تولید می‌کند."""
        return self.report_builder.build(
            self.observations,
            self.failed,
            self.duplicate_groups(),
            self.redirect_tracker.observations,
        )

    def record_failure(self, url: str, error: Exception | str) -> None:
        """خطای یک صفحه را ثبت می‌کند بدون اینکه کل Crawl متوقف شود."""
        self.failed[UrlIdentity.normalize(url)] = str(error)

    def build_observation(
        self, *, url: str, status: int, title: str = "", meta_description: str = "",
        h1_count: int = 0, image_count: int = 0, images_without_alt: int = 0,
        links: list[str] | None = None, security_headers: dict[str, str] | None = None,
        load_time_ms: int = 0, location: str | None = None, canonical_url: str | None = None,
    ) -> PageObservation:
        """مشاهدات Browser/HTTP را به مدل داخلی تبدیل می‌کند."""
        base = urlparse(url)
        internal: list[str] = []
        identities: set[str] = set()
        for link in links or []:
            absolute = UrlIdentity.normalize(urljoin(url, link))
            parsed = urlparse(absolute)
            identity = UrlIdentity.normalize(absolute)
            if parsed.hostname == base.hostname and identity not in identities:
                internal.append(absolute)
                identities.add(identity)
        redirect = self.record_redirect(url, status, location)
        canonical = UrlIdentity.normalize(urljoin(url, canonical_url)) if canonical_url else None
        canonical_observation = self.canonical_analyzer.analyze(url, canonical_url)
        return PageObservation(
            url=UrlIdentity.normalize(url), status=status, title=title, meta_description=meta_description,
            h1_count=h1_count, image_count=image_count, images_without_alt=images_without_alt,
            internal_links=internal, security_headers=security_headers or {}, load_time_ms=load_time_ms,
            redirect=redirect, canonical_url=canonical, canonical=canonical_observation,
        )
