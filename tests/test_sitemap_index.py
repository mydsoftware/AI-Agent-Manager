from agents.site_discovery import SiteDiscovery


class FakeResponse:
    def __init__(self, text: str, status_code: int = 200) -> None:
        self.text = text
        self.status_code = status_code


def test_sitemap_index_discovers_nested_sitemaps_and_urls():
    responses = {
        "https://example.com/robots.txt": FakeResponse("Sitemap: https://example.com/sitemap-index.xml"),
        "https://example.com/sitemap-index.xml": FakeResponse(
            "<sitemapindex>"
            "<sitemap><loc>https://example.com/pages.xml</loc></sitemap>"
            "<sitemap><loc>https://example.com/posts.xml</loc></sitemap>"
            "</sitemapindex>"
        ),
        "https://example.com/pages.xml": FakeResponse(
            "<urlset><url><loc>https://example.com/about</loc></url></urlset>"
        ),
        "https://example.com/posts.xml": FakeResponse(
            "<urlset><url><loc>https://example.com/post-1</loc></url></urlset>"
        ),
    }

    discovery = SiteDiscovery(http_get=lambda url, timeout: responses[url])
    result = discovery.discover("https://example.com")

    assert "https://example.com/sitemap-index.xml" in result["sitemaps"]
    assert "https://example.com/pages.xml" in result["sitemaps"]
    assert "https://example.com/posts.xml" in result["sitemaps"]
    assert result["urls"] == [
        "https://example.com/about",
        "https://example.com/post-1",
    ]
