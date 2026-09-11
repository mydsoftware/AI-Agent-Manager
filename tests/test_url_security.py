import socket

import pytest

from services.browser_qa import BrowserQA
from services.url_security import request_public_http, validate_public_http_url


def test_dns_resolution_to_private_address_is_rejected(monkeypatch):
    """دامنه‌ای که به IP خصوصی Resolve می‌شود باید رد شود."""
    def fake_getaddrinfo(*args, **kwargs):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("10.0.0.7", 443))]

    monkeypatch.setattr(socket, "getaddrinfo", fake_getaddrinfo)
    try:
        validate_public_http_url("https://example.test")
    except ValueError as error:
        assert "IP خصوصی" in str(error)
    else:
        raise AssertionError("دامنه Resolve‌شده به شبکه داخلی نباید پذیرفته شود")


def test_browser_request_guard_aborts_private_redirect_target():
    """Guard مرورگر باید مقصد داخلی Redirect یا Resource را متوقف کند."""
    class FakeRequest:
        def __init__(self, url):
            self.url = url

    class FakeRoute:
        def __init__(self, request):
            self.request = request
            self.aborted = False
            self.continued = False

        def abort(self):
            self.aborted = True

        def continue_(self):
            self.continued = True

    class FakePage:
        def __init__(self):
            self.pattern = None
            self.handler = None

        def route(self, pattern, handler):
            self.pattern = pattern
            self.handler = handler

    page = FakePage()
    BrowserQA()._guard_requests(page)

    assert page.pattern == "**/*"
    assert page.handler is not None

    route = FakeRoute(FakeRequest("http://127.0.0.1:8080/internal"))
    page.handler(route)

    assert route.aborted is True
    assert route.continued is False


def test_sensitive_headers_require_https(monkeypatch):
    """Headerهای حساس نباید حتی در اولین Hop روی HTTP ارسال شوند."""
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *args, **kwargs: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 80))],
    )

    with pytest.raises(ValueError, match="HTTPS"):
        request_public_http(
            "http://example.test/health",
            headers={"X-AI-Agent-Token": "secret-token"},
            sensitive_headers={"X-AI-Agent-Token"},
        )
