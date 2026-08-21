from __future__ import annotations

from urllib.parse import urlparse, urlunparse


class UrlIdentity:
    """یکسان‌سازی هویت URL برای جلوگیری از Crawl تکراری."""

    @staticmethod
    def normalize(url: str) -> str:
        parsed = urlparse(url.strip())
        scheme = parsed.scheme.lower()
        host = (parsed.hostname or "").lower()
        if host.startswith("www."):
            host = host[4:]
        port = parsed.port
        if port and not ((scheme == "http" and port == 80) or (scheme == "https" and port == 443)):
            host = f"{host}:{port}"
        path = parsed.path or "/"
        if path != "/" and path.endswith("/"):
            path = path.rstrip("/")
        return urlunparse((scheme, host, path, "", parsed.query, ""))

    @classmethod
    def equivalent(cls, first: str, second: str) -> bool:
        """بررسی می‌کند دو URL از نظر Crawl یک هویت داشته باشند."""
        return cls.normalize(first) == cls.normalize(second)
