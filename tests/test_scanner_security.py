from agents.public_site_scanner import PublicSiteScanner


def test_invalid_scheme_is_rejected():
    scanner = PublicSiteScanner()
    try:
        scanner.validate_url("ftp://example.com")
    except ValueError as error:
        assert "HTTP/HTTPS" in str(error)
    else:
        raise AssertionError("scheme نامعتبر باید رد شود")


def test_private_address_is_rejected(monkeypatch):
    scanner = PublicSiteScanner()
    monkeypatch.setattr(
        "socket.getaddrinfo",
        lambda *args, **kwargs: [(2, 1, 6, "", ("192.168.1.10", 0))],
    )
    try:
        scanner.validate_url("https://internal.example")
    except PermissionError as error:
        assert "خصوصی" in str(error)
    else:
        raise AssertionError("آدرس خصوصی باید رد شود")


def test_duplicate_urls_are_removed_before_limit():
    scanner = PublicSiteScanner()
    urls = ["https://example.com/a", "https://example.com/a", "https://example.com/b"]
    assert scanner.limit_urls(urls) == ["https://example.com/a", "https://example.com/b"]
