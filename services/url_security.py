"""اعتبارسنجی امن URLهای خروجی برای جلوگیری از SSRF."""

from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse


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

    try:
        addresses = {ipaddress.ip_address(host)}
    except ValueError:
        try:
            addresses = {
                ipaddress.ip_address(info[4][0])
                for info in socket.getaddrinfo(host, parsed.port or (443 if parsed.scheme == "https" else 80), type=socket.SOCK_STREAM)
            }
        except (OSError, ValueError):
            raise ValueError("Host قابل Resolve نیست.") from None

    if not addresses or any(not address.is_global for address in addresses):
        raise ValueError("دسترسی به IP خصوصی، loopback یا شبکه داخلی مجاز نیست.")

    return value
