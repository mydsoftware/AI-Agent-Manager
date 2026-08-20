from unittest.mock import patch

import pytest

from agents.public_site_scanner import PublicSiteScanner


def test_private_and_local_targets_are_rejected():
    with patch("socket.getaddrinfo", return_value=[(2, 0, 0, "", ("127.0.0.1", 0))]):
        with pytest.raises(ValueError, match="داخلی|خصوصی"):
            PublicSiteScanner().scan("https://example.com")


def test_invalid_scheme_is_rejected():
    with pytest.raises(ValueError):
        PublicSiteScanner().scan("ftp://example.com")


def test_scanner_limits_page_count():
    scanner = PublicSiteScanner(max_pages=50)
    assert scanner.max_pages == 10
