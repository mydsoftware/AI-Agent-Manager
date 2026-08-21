from agents.public_site_scanner import PublicSiteScanner
from agents.robots_policy import RobotsPolicy
from agents.site_discovery import SiteDiscovery


class FakeResponse:
    def __init__(self, text: str, status_code: int = 200) -> None:
        self.text = text
        self.status_code = status_code
        self.content = text.encode("utf-8")
        self.headers = {}


def test_disallow_urls_never_enter_queue():
    responses = {
        "https://example.com/robots.txt": FakeResponse(
            "User-agent: *\nDisallow: /private\nAllow: /private/public"
        ),
        "https://example.com/sitemap.xml": FakeResponse(
            "<urlset><url><loc>https://example.com/private/a</loc></url>"
            "<url><loc>https://example.com/private/public/a</loc></url>"
            "<url><loc>https://example.com/about</loc></url></urlset>"
        ),
    }
    discovery = SiteDiscovery(http_get=lambda url, timeout: responses[url])
    scanner = PublicSiteScanner(discovery=discovery, robots_policy=RobotsPolicy())

    scanner.initialize("https://example.com")

    assert "https://example.com/private/a" not in scanner.queue
    assert "https://example.com/private/public/a" in scanner.queue
    assert "https://example.com/about" in scanner.queue


def test_disallow_is_applied_to_links_discovered_during_crawl():
    scanner = PublicSiteScanner(robots_policy=RobotsPolicy())
    scanner.robots_policy.parse("User-agent: *\nDisallow: /admin")
    scanner.robots_discovered = True

    scanner.enqueue([
        "https://example.com/admin",
        "https://example.com/admin/settings",
        "https://example.com/contact",
    ])

    assert list(scanner.queue) == ["https://example.com/contact"]
