from __future__ import annotations

from pathlib import Path

from agents.custom_agent import build_custom_agent
from services.agent_store import AgentStore


def test_custom_agent_store_roundtrip(tmp_path: Path):
    store = AgentStore(str(tmp_path / "agents.db"))
    created = store.create(
        "seo-specialist",
        "متخصص سئو",
        "تحلیل سئو و پیشنهاد اقدام‌های عملی ارائه کن.",
        ["research", "analysis"],
    )
    assert created["name"] == "seo-specialist"
    assert store.get("seo-specialist")["enabled"] == 1
    assert store.list()[0]["description"] == "متخصص سئو"
    assert store.delete("seo-specialist") is True
    assert store.get("seo-specialist") is None


def test_custom_agent_is_declarative():
    agent_class = build_custom_agent(
        "content-writer", "نویسنده", "تو نویسنده هستی.", ["writing"]
    )
    agent = agent_class()
    assert agent.name == "content-writer"
    assert agent.config["system_prompt"] == "تو نویسنده هستی."
    assert agent.config["capabilities"] == "writing"
