from __future__ import annotations

import ipaddress
import socket
import time
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlparse


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
    """اسکنر محدود و فقط خواندنی سایت عمومی برای ممیزی قبل از قرارداد."""
    MAX_PAGES = 10
    DEFAULT_TIMEOUT_MS = 15000

    def validate_url(self, url: str) -> str:
        value = url.strip()
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
            absolute = urljoin(url, link)
            parsed = urlparse(absolute)
            if parsed.hostname == base.hostname and absolute not in internal:
                internal.append(absolute)
        return PageObservation(
            url=url, status=status, title=title, meta_description=meta_description,
            h1_count=h1_count, image_count=image_count, images_without_alt=images_without_alt,
            internal_links=internal, security_headers=security_headers or {}, load_time_ms=load_time_ms,
        )

    def limit_urls(self, urls: list[str]) -> list[str]:
        """تعداد صفحات ممیزی اولیه را محدود می‌کند."""
        return list(dict.fromkeys(urls))[: self.MAX_PAGES]

    def scan_with_browser(self, url: str, *, max_pages: int | None = None, timeout_ms: int | None = None) -> list[PageObservation]:
        """با Playwright فقط صفحات عمومی همان دامنه را می‌خواند."""
        start_url = self.validate_url(url)
        page_limit = min(max_pages or self.MAX_PAGES, self.MAX_PAGES)
        timeout = timeout_ms or self.DEFAULT_TIMEOUT_MS
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as error:
            raise RuntimeError("Playwright نصب نشده است.") from error

        observations: list[PageObservation] = []
        queue = [start_url]
        seen: set[str] = set()
        origin = urlparse(start_url)

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context(ignore_https_errors=False)
            page = context.new_page()
            page.set_default_timeout(timeout)
            page.set_default_navigation_timeout(timeout)

            def document_request(route):
                request = route.request
                if request.resource_type in {"document", "stylesheet", "image", "script", "font"}:
                    return route.continue_()
                return route.abort()

            page.route("**/*", document_request)
            try:
                while queue and len(observations) < page_limit:
                    current = queue.pop(0)
                    if current in seen:
                        continue
                    seen.add(current)
                    parsed = urlparse(current)
                    if parsed.hostname != origin.hostname or parsed.scheme != origin.scheme:
                        continue

                    started = time.perf_counter()
                    response = page.goto(current, wait_until="domcontentloaded")
                    elapsed = int((time.perf_counter() - started) * 1000)
                    if response is None:
                        continue

                    headers = {key.lower(): value for key, value in response.headers.items()}
                    title = page.title()
                    meta = page.locator('meta[name="description"]').first.get_attribute("content") or ""
                    h1_count = page.locator("h1").count()
                    image_count = page.locator("img").count()
                    images_without_alt = page.locator("img:not([alt])").count()
                    links = page.locator("a[href]").evaluate_all("els => els.map(e => e.href)")
                    observation = self.build_observation(
                        url=current,
                        status=response.status,
                        title=title,
                        meta_description=meta,
                        h1_count=h1_count,
                        image_count=image_count,
                        images_without_alt=images_without_alt,
                        links=links,
                        security_headers={key: headers[key] for key in (
                            "content-security-policy", "strict-transport-security", "x-content-type-options",
                            "x-frame-options", "referrer-policy", "permissions-policy"
                        ) if key in headers},
                        load_time_ms=elapsed,
                    )
                    observations.append(observation)
                    for link in observation.internal_links:
                        if link not in seen and link not in queue and len(queue) + len(observations) < page_limit:
                            queue.append(link)
            finally:
                context.close()
                browser.close()
        return observations
