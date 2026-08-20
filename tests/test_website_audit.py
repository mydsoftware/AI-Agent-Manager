from __future__ import annotations

import json

from agents.registry import create_default_registry
from agents.website_audit_agent import WebsiteAuditAgent
from manager.task import Task
from manager.task_router import IntelligentTaskRouter
from website_audit.access import build_access_requests


def test_website_audit_agent_is_registered() -> None:
    registry = create_default_registry()
    assert "website-audit" in registry.names()


def test_router_selects_website_audit_for_site_review() -> None:
    registry = create_default_registry()
    decision = IntelligentTaskRouter(registry).select(
        Task(
            id="1",
            title="بررسی سایت",
            description="GermantechSat.com را از نظر ظاهر، ریسپانسیو و سئو بررسی کن.",
            agent="",
        )
    )
    assert decision.agent == "website-audit"


def test_access_guide_is_step_by_step_and_persian() -> None:
    requests = build_access_requests()
    assert requests
    assert all(item.user_can_do_it for item in requests)
    assert all(item.steps for item in requests)
    assert any("Google Search Console" in item.service for item in requests)


def test_agent_returns_persian_guidance_when_url_is_missing() -> None:
    result = json.loads(
        WebsiteAuditAgent().run(
            Task(id="2", title="ممیزی", description="سایت را بررسی کن.", agent="")
        )
    )
    assert result["وضعیت"] == "نیازمند اطلاعات"
    assert "آدرس" in result["پیام"]
