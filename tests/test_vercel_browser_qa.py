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
