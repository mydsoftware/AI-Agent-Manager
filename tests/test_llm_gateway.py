import io
import json
import urllib.error

import pytest

from manager.llm_gateway import LLMError, LLMGateway


class FakeResponse:
    def __init__(self, payload: dict, status: int = 200) -> None:
        self.payload = payload
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


def test_complete_success(monkeypatch) -> None:
    calls = []

    def fake_urlopen(request, timeout):
        calls.append(request.full_url)
        return FakeResponse(
            {
                "model": "qwen3.5-9b",
                "choices": [{"message": {"content": "ok"}}],
                "usage": {"total_tokens": 3},
            }
        )

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    gateway = LLMGateway(max_retries=0)
    result = gateway.complete([{"role": "user", "content": "hello"}], "qwen3.5-9b")

    assert result.content == "ok"
    assert result.model == "qwen3.5-9b"
    assert result.provider == "lmstudio"
    assert result.usage["total_tokens"] == 3
    assert len(calls) == 1


def test_invalid_response_raises_llm_error(monkeypatch) -> None:
    monkeypatch.setattr("urllib.request.urlopen", lambda *args, **kwargs: FakeResponse({"choices": []}))
    gateway = LLMGateway(max_retries=0)

    with pytest.raises(LLMError):
        gateway.complete([{"role": "user", "content": "hello"}], "qwen3.5-9b")


def test_primary_failure_uses_fallback(monkeypatch) -> None:
    models = []

    def fake_urlopen(request, timeout):
        payload = json.loads(request.data.decode("utf-8"))
        models.append(payload["model"])
        if payload["model"] == "broken-model":
            raise urllib.error.HTTPError(request.full_url, 500, "failure", {}, io.BytesIO(b"server error"))
        return FakeResponse({"model": payload["model"], "choices": [{"message": {"content": "fallback ok"}}]})

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    gateway = LLMGateway(max_retries=0, timeout=1)
    result = gateway.complete([{"role": "user", "content": "hello"}], "broken-model")

    assert result.content == "fallback ok"
    assert models == ["broken-model", "qwen2.5-coder-7b"]
    assert gateway.stats["fallbacks"] == 1


def test_context_error_reduces_context_and_retries(monkeypatch) -> None:
    attempts = []

    def fake_urlopen(request, timeout):
        attempts.append(json.loads(request.data.decode("utf-8")))
        if len(attempts) == 1:
            raise urllib.error.HTTPError(
                request.full_url,
                400,
                "context",
                {},
                io.BytesIO(b"exceeds available context size"),
            )
        return FakeResponse({"model": "qwen3.5-9b", "choices": [{"message": {"content": "recovered"}}]})

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    gateway = LLMGateway(max_retries=0)
    monkeypatch.setattr("time.sleep", lambda *_args: None)
    messages = [
        {"role": "system", "content": "system"},
        {"role": "user", "content": "a" * 10000},
        {"role": "user", "content": "latest"},
    ]
    result = gateway.complete(messages, "qwen3.5-9b")

    assert result.content == "recovered"
    assert gateway.stats["context_reductions"] >= 1
    assert gateway.stats["retries"] == 1
    assert len(attempts) == 2
    assert len(attempts[1]["messages"]) <= len(attempts[0]["messages"])


def test_fallback_candidates_are_capability_aware(monkeypatch) -> None:
    monkeypatch.setenv("LLM_FALLBACK_MODEL_VISION", "vision-fallback")
    monkeypatch.setenv("LLM_FALLBACK_MODEL_CODER", "coder-fallback")
    monkeypatch.setenv("LLM_FALLBACK_MODEL_GENERAL", "general-fallback")
    gateway = LLMGateway()

    assert gateway._fallback_candidates("qwen3-vl-4b-instruct") == ["qwen3-vl-4b-instruct", "vision-fallback"]
    assert gateway._fallback_candidates("qwen2.5-coder-7b") == ["qwen2.5-coder-7b", "coder-fallback"]
    assert gateway._fallback_candidates("qwen3.5-9b") == ["qwen3.5-9b", "general-fallback"]


def test_health_reports_true_and_false(monkeypatch) -> None:
    monkeypatch.setattr("urllib.request.urlopen", lambda *args, **kwargs: FakeResponse({}))
    gateway = LLMGateway(timeout=1)
    assert gateway.health() is True

    def fail(*args, **kwargs):
        raise urllib.error.URLError("offline")

    monkeypatch.setattr("urllib.request.urlopen", fail)
    assert gateway.health() is False
