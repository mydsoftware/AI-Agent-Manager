from __future__ import annotations

import ipaddress
import socket
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlparse, urlunparse

from agents.crawl_state import CrawlState


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


class PublicSiteScanner:
    """Crawler کامل سایت عمومی با صف، حذف URL تکراری و Resume پایدار."""

    def __init__(self) -> None:
        self.queue: deque[str] = deque()
        self.visited: set[str] = set()
        self.observations: list[PageObservation] = []
        self.failed: dict[str, str] = {}

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
        value, _ = urldefrag(url.strip())
        parsed = urlparse(value)
        if not parsed.scheme or not parsed.netloc:
            return value
        path = parsed.path or "/"
        return urlunparse((parsed.scheme.lower(), parsed.netloc.lower(), path, "", parsed.query, ""))

    def enqueue(self, urls: list[str]) -> None:
        """URLهای جدید را بدون تکرار وارد صف Crawl می‌کند."""
        for url in urls:
            normalized = self.normalize_url(url)
            if normalized and normalized not in self.visited and normalized not in self.queue:
                self.queue.append(normalized)

    def resume(self, urls: list[str]) -> None:
        """Crawl را از URLهای ذخیره‌شده ادامه می‌دهد."""
        self.enqueue(urls)

    def save_state(self, path: str | Path) -> None:
        """وضعیت فعلی صف، صفحات و خطاها را ذخیره می‌کند."""
        CrawlState(
            queue=list(self.queue),
            visited=sorted(self.visited),
            failed=dict(self.failed),
        ).save(path)

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

    def record_observation(self, observation: PageObservation) -> None:
        """نتیجه صفحه را ثبت و لینک‌های داخلی آن را وارد صف می‌کند."""
        self.observations.append(observation)
        self.enqueue(observation.internal_links)

    def record_failure(self, url: str, error: Exception | str) -> None:
        """خطای یک صفحه را ثبت می‌کند بدون اینکه کل Crawl متوقف شود."""
        self.failed[self.normalize_url(url)] = str(error)

    def build_observation(
        self, *, url: str, status: int, title: str = "", meta_description: str = "",
        h1_count: int = 0, image_count: int = 0, images_without_alt: int = 0,
        links: list[str] | None = None, security_headers: dict[str, str] | None = None,
        load_time_ms: int = 0,
    ) -> PageObservation:
        """مشاهدات Browser را به مدل داخلی تبدیل می‌کند."""
        base = urlparse(url)
        internal: list[str] = []
        for link in links or []:
            absolute = self.normalize_url(urljoin(url, link))
            parsed = urlparse(absolute)
            if parsed.hostname == base.hostname and absolute not in internal:
                internal.append(absolute)
        return PageObservation(
            url=self.normalize_url(url), status=status, title=title, meta_description=meta_description,
            h1_count=h1_count, image_count=image_count, images_without_alt=images_without_alt,
            internal_links=internal, security_headers=security_headers or {}, load_time_ms=load_time_ms,
        )
