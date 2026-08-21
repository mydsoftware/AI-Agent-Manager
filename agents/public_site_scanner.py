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
from agents.site_audit_html import SiteAuditHtmlRenderer
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

    # محدودیت پیش‌فرض وجود ندارد؛ Crawl تا خالی شدن صف ادامه می‌یابد.
    # max_pages فقط محدودکننده اختیاری است.
    MAX_PAGES: int | None = None

    def __init__(
        self,
        discovery: SiteDiscovery | None = None,
        robots_policy: RobotsPolicy | None = None,
        max_pages: int | None = None,
        http_get=None,
    ) -> None:
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
        self.html_renderer = SiteAuditHtmlRenderer()
        self.robots_discovered = False
        # None یعنی بدون سقف؛ عدد مثبت یعنی توقف پس از N صفحه
        self.max_pages = max_pages if max_pages is not None else self.MAX_PAGES
        self.http_get = http_get

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

    def limit_urls(self, urls: list[str]) -> list[str]:
        """URLها را یکتا می‌کند و در صورت تعیین max_pages محدود می‌کند."""
        unique: list[str] = []
        seen: set[str] = set()
        for url in urls:
            normalized = UrlIdentity.normalize(url)
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            unique.append(normalized)
            if self.max_pages is not None and len(unique) >= self.max_pages:
                break
        return unique

    def _fetch_page(self, url: str) -> PageObservation:
        """یک صفحه را با http_get یا پاسخ شبیه‌سازی‌شده واکشی می‌کند."""
        if self.http_get is None:
            return self.build_observation(url=url, status=200, title="", links=[])
        try:
            response = self.http_get(url)
        except Exception as error:
            self.record_failure(url, error)
            return self.build_observation(url=url, status=0, title="")
        status = int(getattr(response, "status_code", getattr(response, "status", 200)) or 200)
        text = getattr(response, "text", "") or ""
        headers = dict(getattr(response, "headers", {}) or {})
        location = headers.get("Location") or headers.get("location")
        import re
        title_m = re.search(r"<title[^>]*>(.*?)</title>", text, re.I | re.S)
        title = re.sub(r"\s+", " ", title_m.group(1)).strip() if title_m else ""
        meta_m = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)["\']', text, re.I)
        if not meta_m:
            meta_m = re.search(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+name=["\']description["\']', text, re.I)
        meta_description = meta_m.group(1).strip() if meta_m else ""
        can_m = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']', text, re.I)
        if not can_m:
            can_m = re.search(r'<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\']canonical["\']', text, re.I)
        canonical_url = can_m.group(1) if can_m else None
        links = re.findall(r'<a[^>]+href=["\']([^"\']+)["\']', text, re.I)
        h1_count = len(re.findall(r"<h1\b", text, re.I))
        imgs = re.findall(r"<img\b[^>]*>", text, re.I)
        image_count = len(imgs)
        images_without_alt = sum(1 for img in imgs if not re.search(r'alt=["\'][^"\']+["\']', img, re.I))
        security_keys = {
            "content-security-policy", "strict-transport-security",
            "x-content-type-options", "x-frame-options", "referrer-policy",
        }
        security_headers = {k: v for k, v in headers.items() if k.lower() in security_keys}
        return self.build_observation(
            url=url, status=status, title=title, meta_description=meta_description,
            h1_count=h1_count, image_count=image_count, images_without_alt=images_without_alt,
            links=links, security_headers=security_headers, location=location,
            canonical_url=canonical_url,
        )

    def scan(self, start_url: str, *, max_pages: int | None = None) -> SiteAuditReport:
        """Crawl کامل سایت از URL شروع؛ تا خالی شدن صف ادامه می‌دهد مگر max_pages محدود کند.

        محافظت SSRF حفظ می‌شود. max_pages فقط محدودکننده اختیاری است.
        """
        if max_pages is not None:
            self.max_pages = max_pages
        root = self.validate_url(start_url)
        self.initialize(root)
        while True:
            if self.max_pages is not None and len(self.observations) >= self.max_pages:
                break
            url = self.next_url()
            if url is None:
                break
            try:
                # SSRF: هر URL جدید نیز قبل از واکشی اعتبارسنجی می‌شود
                self.validate_url(url)
            except (ValueError, PermissionError) as error:
                self.record_failure(url, error)
                continue
            observation = self._fetch_page(url)
            self.record_observation(observation)
        return self.generate_report()

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

    def generate_html_report(self, path: str | Path, title: str = "گزارش ممیزی سایت") -> Path:
        """گزارش HTML فارسی را تولید و در مسیر مشخص ذخیره می‌کند."""
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        html = self.html_renderer.render(self.generate_report(), title=title)
        destination.write_text(html, encoding="utf-8")
        return destination

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
