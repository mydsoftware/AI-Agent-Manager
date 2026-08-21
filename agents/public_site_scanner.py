from __future__ import annotations

import ipaddress
import socket
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
