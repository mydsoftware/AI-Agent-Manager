from unittest.mock import patch

import pytest

from agents.public_site_scanner import PublicSiteScanner


def test_private_and_local_targets_are_rejected():
    with patch("socket.getaddrinfo", return_value=[(2, 0, 0, "", ("127.0.0.1", 0))]):
        with pytest.raises(PermissionError, match="داخلی|خصوصی"):
            PublicSiteScanner().scan("https://example.com")


def test_invalid_scheme_is_rejected():
    with pytest.raises(ValueError):
        PublicSiteScanner().scan("ftp://example.com")


def test_scanner_accepts_optional_max_pages():
    scanner = PublicSiteScanner(max_pages=50)
    assert scanner.max_pages == 50


def test_scanner_default_has_no_page_cap():
    scanner = PublicSiteScanner()
    assert scanner.max_pages is None
    assert PublicSiteScanner.MAX_PAGES is None


def test_limit_urls_respects_max_pages():
    scanner = PublicSiteScanner(max_pages=3)
    urls = [f"https://example.com/{i}" for i in range(10)]
    limited = scanner.limit_urls(urls)
    assert len(limited) == 3


def test_limit_urls_without_cap_keeps_all_unique():
    scanner = PublicSiteScanner()
    urls = [f"https://example.com/{i}" for i in range(5)] + ["https://example.com/0"]
    limited = scanner.limit_urls(urls)
    assert len(limited) == 5
