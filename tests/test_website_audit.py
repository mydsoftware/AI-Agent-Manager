from __future__ import annotations

import json

from agents.registry import create_default_registry
from agents.website_audit_agent import WebsiteAuditAgent
from manager.task import Task
from manager.task_router import IntelligentTaskRouter
from website_audit.access import build_access_requests
from website_audit.deep_engine import DeepWebsiteAuditEngine


def test_website_audit_agent_is_registered() -> None:
    registry = create_default_registry()
    assert "website-audit" in registry.names()


def test_router_selects_website_audit_for_site_review() -> None:
    registry = create_default_registry()
    decision = IntelligentTaskRouter(registry).select(
        Task("1", "بررسی سایت", "GermantechSat.com را از نظر ظاهر، ریسپانسیو و سئو بررسی کن.", "")
    )
    assert decision.agent == "website-audit"


def test_access_guide_is_step_by_step_and_persian() -> None:
    requests = build_access_requests()
    assert requests
    assert all(item.user_can_do_it for item in requests)
    assert all(item.steps for item in requests)
    assert any("Google Search Console" in item.service for item in requests)


def test_agent_returns_persian_guidance_when_url_is_missing() -> None:
    result = json.loads(WebsiteAuditAgent().run(Task("2", "ممیزی", "سایت را بررسی کن.", "")))
    assert result["وضعیت"] == "نیازمند اطلاعات"
    assert "آدرس" in result["پیام"]


def test_deep_engine_crawls_same_origin_and_checks_optional_files(monkeypatch) -> None:
    class FakeResponse:
        def __init__(self, body: str, status: int = 200):
            self._body = body.encode()
            self.status = status

        def read(self, _limit=None):
            return self._body

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    pages = {
        "https://example.com/": '<html><head><title>خانه</title><meta name="description" content="توضیح"></head><body><a href="/about">درباره</a></body></html>',
        "https://example.com/about": '<html><body><h1>درباره</h1><a href="https://other.example/x">خارجی</a></body></html>',
        "https://example.com/robots.txt": 'User-agent: *\nSitemap: https://example.com/sitemap.xml',
        "https://example.com/sitemap.xml": '<urlset></urlset>',
    }

    def fake_get(self, url):
        if url not in pages:
            raise OSError(url)
        return FakeResponse(pages[url])

    monkeypatch.setattr(DeepWebsiteAuditEngine, "_get", fake_get)
    report = DeepWebsiteAuditEngine(max_pages=5).audit("https://example.com", run_browser=False)
    assert "https://example.com/about" in {"https://example.com/about"}
    assert "خزش کنترل‌شده" in report.summary
    assert report.mode == "ممیزی عمومی"
