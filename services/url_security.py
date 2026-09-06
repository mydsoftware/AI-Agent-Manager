"""اعتبارسنجی و درخواست امن URLهای خروجی برای جلوگیری از SSRF."""

from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urljoin, urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3 import PoolManager


def _resolve_public_addresses(host: str, port: int) -> list[ipaddress._BaseAddress]:
    """Host را Resolve می‌کند و فقط IPهای عمومی را برای اتصال مجاز نگه می‌دارد."""
    try:
        addresses = {ipaddress.ip_address(host)}
    except ValueError:
        try:
            addresses = {
                ipaddress.ip_address(info[4][0])
                for info in socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
            }
        except (OSError, ValueError):
            raise ValueError("Host قابل Resolve نیست.") from None

    if not addresses or any(not address.is_global for address in addresses):
        raise ValueError("دسترسی به IP خصوصی، loopback یا شبکه داخلی مجاز نیست.")
    return sorted(addresses, key=str)


def validate_public_http_url(url: str) -> str:
    """URL را بررسی می‌کند و مقصدهای localhost، شبکه داخلی و IP خصوصی را رد می‌کند."""
    value = url.strip()
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("URL فقط باید با http:// یا https:// شروع شود.")
    if not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("URL باید یک Host معتبر عمومی و بدون Credential داشته باشد.")

    host = parsed.hostname.rstrip(".").lower()
    if host in {"localhost", "localhost.localdomain", "0.0.0.0", "::1"} or host.endswith(".localhost"):
        raise ValueError("دسترسی به localhost و مقصدهای محلی مجاز نیست.")

    _resolve_public_addresses(host, parsed.port or (443 if parsed.scheme == "https" else 80))
    return value


class _PinnedHostAdapter(HTTPAdapter):
    """Adapterی که اتصال را به IP Resolve‌شده Pin می‌کند و SNI/گواهی را روی Host اصلی نگه می‌دارد."""

    def __init__(self, host: str, ip: str, **kwargs) -> None:
        """Adapter را با Host اصلی و IP عمومی Resolve‌شده آماده می‌کند."""
        self.host = host
        self.ip = ip
        super().__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs) -> None:
        """Pool را به IP ثابت متصل می‌کند بدون غیرفعال‌کردن بررسی TLS hostname."""
        pool_kwargs["assert_hostname"] = self.host
        pool_kwargs["server_hostname"] = self.host
        self.poolmanager = PoolManager(num_pools=connections, maxsize=maxsize, block=block, **pool_kwargs)

    def get_connection(self, url, proxies=None):
        """Connection Pool مربوط به IP ثابت را برمی‌گرداند."""
        parsed = urlparse(url)
        scheme = parsed.scheme
        port = parsed.port or (443 if scheme == "https" else 80)
        return self.poolmanager.connection_from_host(self.ip, port=port, scheme=scheme)


def request_public_http(
    url: str,
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    timeout: int = 15,
    max_redirects: int = 3,
) -> requests.Response:
    """درخواست HTTP(S) را با IP Resolve‌شده و Redirectهای دوباره‌اعتبارسنجی‌شده اجرا می‌کند."""
    current = validate_public_http_url(url)
    session = requests.Session()
    try:
        for _ in range(max_redirects + 1):
            parsed = urlparse(current)
            host = parsed.hostname or ""
            port = parsed.port or (443 if parsed.scheme == "https" else 80)
            ip = str(_resolve_public_addresses(host, port)[0])
            adapter = _PinnedHostAdapter(host, ip)
            session.mount(f"{parsed.scheme}://", adapter)
            request_headers = dict(headers or {})
            request_headers["Host"] = host if parsed.port is None else f"{host}:{parsed.port}"
            response = session.request(
                method,
                current,
                headers=request_headers,
                timeout=timeout,
                allow_redirects=False,
            )
            if response.status_code not in {301, 302, 303, 307, 308}:
                return response
            location = response.headers.get("Location")
            if not location:
                return response
            next_url = validate_public_http_url(urljoin(current, location))
            response.close()
            current = next_url
        raise ValueError("تعداد Redirectهای URL از حد مجاز بیشتر است.")
    finally:
        session.close()
