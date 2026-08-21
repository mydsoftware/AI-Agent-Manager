from __future__ import annotations

import re
from urllib.parse import urljoin, urlparse


class SiteDiscovery:
    """کشف URLهای سایت از robots.txt و Sitemap/Sitemap Index برای Crawl کامل."""

    MAX_SITEMAP_DEPTH = 10

    def __init__(self, http_get=None) -> None:
        self.http_get = http_get

    def discover(self, base_url: str) -> dict[str, list[str]]:
        """robots.txt و همه Sitemapهای قابل کشف را بررسی می‌کند."""
        base = base_url.rstrip("/") + "/"
        hostname = urlparse(base).hostname
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

        visited_sitemaps: set[str] = set()
        pending = list(dict.fromkeys(result["sitemaps"]))
        depth = 0
        while pending and depth < self.MAX_SITEMAP_DEPTH:
            current = pending.pop(0)
            if current in visited_sitemaps:
                continue
            visited_sitemaps.add(current)
            xml = self._get_text(current)
            if xml is None:
                depth += 1
                continue
            for candidate in self._extract_locs(xml):
                parsed = urlparse(candidate)
                if parsed.scheme not in {"http", "https"} or parsed.hostname != hostname:
                    continue
                if self._looks_like_sitemap(candidate, xml):
                    if candidate not in visited_sitemaps and candidate not in pending:
                        pending.append(candidate)
                    if candidate not in result["sitemaps"]:
                        result["sitemaps"].append(candidate)
                else:
                    result["urls"].append(candidate)
            depth += 1

        result["sitemaps"] = list(dict.fromkeys(result["sitemaps"]))
        result["urls"] = list(dict.fromkeys(result["urls"]))
        return result

    @staticmethod
    def _extract_locs(xml: str) -> list[str]:
        """مقدارهای loc را از XML Sitemap استخراج می‌کند."""
        return [value.strip() for value in re.findall(r"<loc[^>]*>\s*(.*?)\s*</loc>", xml, flags=re.I | re.S)]

    @staticmethod
    def _looks_like_sitemap(candidate: str, parent_xml: str) -> bool:
        """تشخیص می‌دهد loc مربوط به Sitemap یا URL معمولی است."""
        root = re.search(r"<\s*(sitemapindex|urlset)\b", parent_xml, flags=re.I)
        if root and root.group(1).lower() == "sitemapindex":
            return True
        return candidate.lower().endswith((".xml", ".xml.gz"))

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
