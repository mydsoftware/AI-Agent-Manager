from __future__ import annotations

import json

from agents.developer_agent import DeveloperAgent
from agents.research_agent import ResearchAgent
from manager.llm_gateway import LLMGateway
from manager.model_router import ModelRouter
from manager.task import Task


def test_model_router_defaults_match_local_stack():
    router = ModelRouter()
    assert router.resolve("developer") == "qwen3.5-9b"
    assert router.resolve("coder") == "qwen2.5-coder-7b"
    assert router.resolve("vision") == "qwen3-vl-4b-instruct"


def test_gateway_parses_openai_compatible_response(monkeypatch):
    class Response:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return json.dumps({
                "model": "qwen3.5-9b",
                "choices": [{"message": {"content": "پاسخ محلی"}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 4},
            }).encode("utf-8")

    monkeypatch.setattr("urllib.request.urlopen", lambda *args, **kwargs: Response())
    gateway = LLMGateway(base_url="http://127.0.0.1:1234/v1", max_retries=0)
    result = gateway.complete([{"role": "user", "content": "سلام"}], "qwen3.5-9b")

    assert result.content == "پاسخ محلی"
    assert result.model == "qwen3.5-9b"
    assert gateway.stats["success"] == 1


def test_developer_keeps_structured_workflow_without_llm_call():
    class NeverCalled:
        def complete(self, *args, **kwargs):
            raise AssertionError("structured engineering tasks must not call LLM")

    task = Task(
        id="1",
        title="ساخت",
        description=json.dumps({
            "repository": "mydsoftware/example",
            "branch": "feature/test",
            "change": "add endpoint",
        }),
        agent="developer",
    )
    result = DeveloperAgent(NeverCalled()).run(task)
    assert json.loads(result)["engineering_loop"] is True


def test_research_agent_uses_local_llm(monkeypatch):
    class FakeGateway:
        def complete(self, messages, model, **kwargs):
            assert model == "qwen3.5-9b"
            return type("Response", (), {"content": "نتیجه تحقیق"})()

    task = Task(id="r1", title="تحقیق", description="مزایای معماری چندایجنتی را تحلیل کن", agent="research")
    result = ResearchAgent(FakeGateway()).run(task)
    assert result == "نتیجه تحقیق"
