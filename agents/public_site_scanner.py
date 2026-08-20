from __future__ import annotations

import ipaddress
import socket
from dataclasses import dataclass, field
from time import perf_counter
from urllib.parse import urljoin, urlparse


@dataclass(frozen=True)
class PageObservation:
    """مشاهدات خواندنی یک صفحه عمومی."""

    url: str
    status: int | None
    title: str
    meta_description: str
    h1_count: int
    image_count: int
    images_without_alt: int
    internal_links: tuple[str, ...]
    security_headers: tuple[str, ...]
    load_ms: int | None


@dataclass
class PublicSiteScan:
    """نتیجه Crawl محدود صفحات عمومی سایت."""

    start_url: str
    pages: list[PageObservation] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class PublicSiteScanner:
    """اسکنر خواندنی با Playwright؛ بدون ورود، ارسال فرم یا تغییر سایت."""

    def __init__(self, max_pages: int = 5, timeout_ms: int = 15000) -> None:
        self.max_pages = max(1, min(max_pages, 10))
        self.timeout_ms = timeout_ms

    @staticmethod
    def _validate_public_url(url: str) -> str:
        parsed = urlparse(url.strip())
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("فقط URLهای HTTP/HTTPS معتبر هستند.")
        host = parsed.hostname
        try:
            addresses = {info[4][0] for info in socket.getaddrinfo(host, None)}
        except socket.gaierror as error:
            raise ValueError("دامنه قابل دسترسی نیست.") from error
        for address in addresses:
            ip = ipaddress.ip_address(address)
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_unspecified:
                raise ValueError("اسکن آدرس‌های داخلی یا خصوصی مجاز نیست.")
        return parsed._replace(fragment="").geturl()

    def scan(self, url: str) -> PublicSiteScan:
        start_url = self._validate_public_url(url)
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return PublicSiteScan(start_url, errors=["Playwright نصب نیست."])

        origin = urlparse(start_url).netloc
        queue = [start_url]
        visited: set[str] = set()
        result = PublicSiteScan(start_url)

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                context = browser.new_context()
                page = context.new_page()
                while queue and len(result.pages) < self.max_pages:
                    current = queue.pop(0)
                    normalized = current.rstrip("/") or current
                    if normalized in visited:
                        continue
                    visited.add(normalized)
                    try:
                        started = perf_counter()
                        response = page.goto(current, wait_until="domcontentloaded", timeout=self.timeout_ms)
                        load_ms = int((perf_counter() - started) * 1000)
                        links = page.locator("a[href]")
                        internal: list[str] = []
                        for index in range(min(links.count(), 100)):
                            href = links.nth(index).get_attribute("href")
                            if not href:
                                continue
                            absolute = urljoin(current, href).split("#", 1)[0]
                            parsed = urlparse(absolute)
                            if parsed.scheme in {"http", "https"} and parsed.netloc == origin:
                                if absolute.rstrip("/") not in visited and absolute not in queue:
                                    queue.append(absolute)
                                internal.append(absolute)

                        headers = response.all_headers() if response else {}
                        security = tuple(
                            name
                            for name in (
                                "content-security-policy",
                                "strict-transport-security",
                                "x-content-type-options",
                                "x-frame-options",
                                "referrer-policy",
                            )
                            if name in headers
                        )
                        images = page.locator("img")
                        missing_alt = sum(
                            1
                            for index in range(min(images.count(), 200))
                            if images.nth(index).get_attribute("alt") is None
                        )
                        result.pages.append(
                            PageObservation(
                                url=current,
                                status=response.status if response else None,
                                title=page.title().strip(),
                                meta_description=(
                                    page.locator('meta[name="description"]').first.get_attribute("content") or ""
                                ).strip(),
                                h1_count=page.locator("h1").count(),
                                image_count=images.count(),
                                images_without_alt=missing_alt,
                                internal_links=tuple(dict.fromkeys(internal)),
                                security_headers=security,
                                load_ms=load_ms,
                            )
                        )
                    except Exception as error:
                        result.errors.append(f"{current}: {type(error).__name__}")
                context.close()
            finally:
                browser.close()
        return result
