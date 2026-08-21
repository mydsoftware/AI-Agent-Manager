from __future__ import annotations

from urllib.parse import urljoin, urlparse


class SiteDiscovery:
    """کشف URLهای سایت از robots.txt و sitemap برای شروع Crawl کامل."""

    def __init__(self, http_get=None) -> None:
        self.http_get = http_get

    def discover(self, base_url: str) -> dict[str, list[str]]:
        """robots.txt و sitemapهای معرفی‌شده را می‌خواند و URLهای معتبر را برمی‌گرداند."""
        base = base_url.rstrip("/") + "/"
        result = {"robots": [], "sitemaps": [], "urls": []}
        robots_url = urljoin(base, "robots.txt")
        robots = self._get_text(robots_url)
        if robots is not None:
            result["robots"] = robots.splitlines()
            for line in robots.splitlines():
                if line.lower().startswith("sitemap:"):
                    sitemap = line.split(":", 1)[1].strip()
                    if sitemap:
                        result["sitemaps"].append(urljoin(base, sitemap))
        if not result["sitemaps"]:
            result["sitemaps"].append(urljoin(base, "sitemap.xml"))

        for sitemap_url in list(dict.fromkeys(result["sitemaps"])):
            xml = self._get_text(sitemap_url)
            if xml is None:
                continue
            for token in xml.replace("<loc>", "\n").replace("</loc>", "\n").splitlines():
                candidate = token.strip()
                parsed = urlparse(candidate)
                if parsed.scheme in {"http", "https"} and parsed.hostname == urlparse(base).hostname:
                    result["urls"].append(candidate)
        result["urls"] = list(dict.fromkeys(result["urls"]))
        return result

    def _get_text(self, url: str) -> str | None:
        if self.http_get is None:
            return None
        try:
            response = self.http_get(url, timeout=15)
            if getattr(response, "status_code", 0) >= 400:
                return None
            return str(getattr(response, "text", ""))
        except Exception:
            return None
