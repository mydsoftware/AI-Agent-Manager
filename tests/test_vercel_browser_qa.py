from api.vercel_api import register_vercel_api
from services.browser_qa import BrowserQA
from services.url_security import validate_public_http_url
from services.vercel_deployment import VercelConfig, VercelDeploymentService


def test_vercel_status_does_not_expose_token():
    result = VercelDeploymentService(VercelConfig(token="secret-token")).status()
    assert result == {"configured": True, "provider": "vercel", "api_base_url": "https://api.vercel.com"}
    assert "secret-token" not in str(result)


def test_vercel_rejects_empty_project():
    service = VercelDeploymentService(VercelConfig(token="token"))
    try:
        service.project("")
    except ValueError as error:
        assert "project_id" in str(error)
    else:
        raise AssertionError("باید برای project_id خالی خطا رخ دهد")


def test_browser_qa_requires_http_url():
    qa = BrowserQA()
    try:
        qa.run_smoke("javascript:alert(1)")
    except ValueError as error:
        assert "http" in str(error)
    else:
        raise AssertionError("URL ناامن باید رد شود")


def test_browser_qa_blocks_local_targets():
    """ورودی اصلی QA باید مقصدهای محلی را قبل از Browser/Navigation رد کند."""
    qa = BrowserQA()
    for url in ("http://127.0.0.1:8080", "http://localhost:3000", "http://10.0.0.1"):
        try:
            qa.run_smoke(url)
        except ValueError:
            pass
        else:
            raise AssertionError(f"باید مقصد محلی رد شود: {url}")


def test_public_url_validator_rejects_local_targets():
    """Validator مستقل نیز باید برای تست واحد URL security پوشش داده شود."""
    for url in ("http://127.0.0.1:8080", "http://localhost:3000", "http://10.0.0.1"):
        try:
            validate_public_http_url(url)
        except ValueError:
            pass
        else:
            raise AssertionError(f"باید مقصد محلی رد شود: {url}")


def test_browser_qa_reports_not_configured():
    result = BrowserQA().run_smoke("https://example.com")
    assert result["status"] == "not_configured"
    assert result["checks"] == []


def test_browser_qa_creates_context_with_service_workers_blocked(monkeypatch):
    """QA واقعی باید Service Worker را پیش از navigation مسدود کند."""
    monkeypatch.setattr("services.browser_qa.validate_public_http_url", lambda url: url)

    class FakePage:
        def route(self, *_args):
            pass

        def goto(self, *_args, **_kwargs):
            return type("Response", (), {"status": 200})()

        def title(self):
            return "QA"

    class FakeContext:
        def __init__(self):
            self.page = FakePage()

        def new_page(self):
            return self.page

        def close(self):
            pass

    class FakeBrowser:
        def __init__(self):
            self.kwargs = None

        def new_context(self, **kwargs):
            self.kwargs = kwargs
            return FakeContext()

        def close(self):
            pass

    browser = FakeBrowser()
    result = BrowserQA(lambda: browser).run_smoke("https://example.com")
    assert result["status"] == "passed"
    assert browser.kwargs == {"service_workers": "block"}


def test_browser_qa_fails_closed_without_network_proxy():
    """Runtime production mode نباید Browser را بدون egress policy شبکه اجرا کند."""
    called = []

    def browser_factory():
        called.append(True)
        raise AssertionError("browser نباید بدون proxy شبکه ساخته شود")

    result = BrowserQA(browser_factory=browser_factory, require_egress_proxy=True).run_smoke("https://example.com")
    assert result["status"] == "failed"
    assert result["network_egress"] == "required_proxy_not_configured"
    assert called == []


def test_browser_qa_uses_configured_network_proxy(monkeypatch):
    """وقتی Proxy تنظیم شده، BrowserContext باید Proxy و Service Worker blocking را دریافت کند."""
    monkeypatch.setattr("services.browser_qa.validate_public_http_url", lambda url: url)

    class FakePage:
        def route(self, *_args):
            pass

        def goto(self, *_args, **_kwargs):
            return type("Response", (), {"status": 200})()

        def title(self):
            return "QA"

    class FakeContext:
        def new_page(self):
            return FakePage()

        def close(self):
            pass

    class FakeBrowser:
        def __init__(self):
            self.kwargs = None

        def new_context(self, **kwargs):
            self.kwargs = kwargs
            return FakeContext()

        def close(self):
            pass

    browser = FakeBrowser()
    result = BrowserQA(
        browser_factory=lambda: browser,
        egress_proxy="http://127.0.0.1:18080",
        require_egress_proxy=True,
    ).run_smoke("https://example.com")
    assert result["status"] == "passed"
    assert browser.kwargs == {
        "service_workers": "block",
        "proxy": {"server": "http://127.0.0.1:18080"},
    }


def test_deployment_api_requires_authentication(monkeypatch):
    monkeypatch.setenv("MANAGER_API_TOKEN", "test-manager-token")
    from flask import Flask
    app = Flask(__name__)
    register_vercel_api(app, VercelDeploymentService(VercelConfig(token="vercel-token")))
    client = app.test_client()
    assert client.get("/api/vercel/status").status_code == 401
    assert client.get("/api/vercel/status", headers={"X-Manager-API-Key": "test-manager-token"}).status_code == 200


def test_deployment_api_denies_access_when_server_token_is_unconfigured(monkeypatch):
    monkeypatch.delenv("MANAGER_API_TOKEN", raising=False)
    from flask import Flask
    app = Flask(__name__)
    register_vercel_api(app)
    assert app.test_client().post("/api/browser-qa/smoke", json={"url": "https://example.com"}).status_code == 401
