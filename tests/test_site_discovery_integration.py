from agents.public_site_scanner import PublicSiteScanner
from agents.site_discovery import SiteDiscovery


class FakeResponse:
    def __init__(self, text: str, status_code: int = 200) -> None:
        self.text = text
        self.status_code = status_code


def test_discovery_urls_are_added_to_scanner_queue():
    responses = {
        "https://example.com/robots.txt": FakeResponse(
            "User-agent: *\nAllow: /\nSitemap: https://example.com/custom-sitemap.xml"
        ),
        "https://example.com/custom-sitemap.xml": FakeResponse(
            "<urlset><url><loc>https://example.com/about</loc></url>"
            "<url><loc>https://example.com/contact#team</loc></url></urlset>"
        ),
    }

    discovery = SiteDiscovery(http_get=lambda url, timeout: responses[url])
    scanner = PublicSiteScanner(discovery=discovery)

    result = scanner.initialize("https://example.com")

    assert result["sitemaps"] == ["https://example.com/custom-sitemap.xml"]
    assert list(scanner.queue) == [
        "https://example.com/",
        "https://example.com/about",
        "https://example.com/contact",
    ]


def test_discovery_ignores_sitemap_urls_from_other_domains():
    responses = {
        "https://example.com/robots.txt": FakeResponse(
            "Sitemap: https://example.com/sitemap.xml"
        ),
        "https://example.com/sitemap.xml": FakeResponse(
            "<urlset><url><loc>https://example.com/a</loc></url>"
            "<url><loc>https://other.example/b</loc></url></urlset>"
        ),
    }

    discovery = SiteDiscovery(http_get=lambda url, timeout: responses[url])
    scanner = PublicSiteScanner(discovery=discovery)
    scanner.initialize("https://example.com")

    assert "https://example.com/a" in scanner.queue
    assert "https://other.example/b" not in scanner.queue
