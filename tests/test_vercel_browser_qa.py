from services.browser_qa import BrowserQA
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


def test_browser_qa_reports_not_configured():
    result = BrowserQA().run_smoke("https://example.com")
    assert result["status"] == "not_configured"
    assert result["checks"] == []
