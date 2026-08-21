import gzip

from agents.site_discovery import SiteDiscovery


class FakeResponse:
    def __init__(self, content: bytes, status_code: int = 200, headers=None) -> None:
        self.content = content
        self.status_code = status_code
        self.headers = headers or {}
        self.text = ""


def test_gzip_sitemap_is_decompressed_and_parsed():
    payload = b"<urlset><url><loc>https://example.com/product-1</loc></url></urlset>"
    responses = {
        "https://example.com/robots.txt": FakeResponse(
            b"Sitemap: https://example.com/sitemap.xml.gz"
        ),
        "https://example.com/sitemap.xml.gz": FakeResponse(gzip.compress(payload)),
    }

    discovery = SiteDiscovery(http_get=lambda url, timeout: responses[url])
    result = discovery.discover("https://example.com")

    assert "https://example.com/sitemap.xml.gz" in result["sitemaps"]
    assert result["urls"] == ["https://example.com/product-1"]


def test_gzip_content_encoding_is_supported():
    payload = b"<urlset><url><loc>https://example.com/a</loc></url></urlset>"
    responses = {
        "https://example.com/robots.txt": FakeResponse(
            b"Sitemap: https://example.com/sitemap"
        ),
        "https://example.com/sitemap": FakeResponse(
            gzip.compress(payload), headers={"Content-Encoding": "gzip"}
        ),
    }

    discovery = SiteDiscovery(http_get=lambda url, timeout: responses[url])
    result = discovery.discover("https://example.com")

    assert result["urls"] == ["https://example.com/a"]
