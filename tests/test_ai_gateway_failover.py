from __future__ import annotations

import pytest

from ai_gateway.gateway import AIGateway
from ai_gateway.models import (
    AIMessage,
    AIProviderAdapter,
    AIProviderError,
    AIRequest,
    AIResponse,
)


class FakeAdapter(AIProviderAdapter):
    def __init__(
        self,
        name: str,
        *,
        healthy: bool = True,
        probe_ok: bool = True,
        failure: bool = False,
    ) -> None:
        self.name = name
        self.healthy = healthy
        self.probe_ok = probe_ok
        self.failure = failure
        self.calls = 0
        self.probe_calls = 0

    def health(self) -> bool:
        return self.healthy

    def probe(self) -> bool:
        self.probe_calls += 1
        return self.probe_ok

    def complete(self, request: AIRequest) -> AIResponse:
        self.calls += 1
        if self.failure:
            raise AIProviderError(f"{self.name}: خطای شبیه‌سازی‌شده")
        return AIResponse(
            content=f"پاسخ از {self.name}",
            provider=self.name,
            model=request.model,
        )


def make_request() -> AIRequest:
    return AIRequest(messages=[AIMessage(role="user", content="سلام")])


def test_omniroute_is_used_when_healthy() -> None:
    omni = FakeAdapter("omniroute")
    free = FakeAdapter("freellmapi")
    gateway = AIGateway([omni, free])

    response = gateway.complete(make_request())

    assert response.provider == "omniroute"
    assert omni.calls == 1
    assert free.calls == 0


def test_fallback_to_freellmapi_when_omniroute_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AI_GATEWAY_ORDER", "omniroute,freellmapi")
    omni = FakeAdapter("omniroute", failure=True)
    free = FakeAdapter("freellmapi")
    gateway = AIGateway([omni, free])

    response = gateway.complete(make_request())

    assert response.provider == "freellmapi"
    assert omni.calls == 1
    assert free.calls == 1


def test_unhealthy_primary_is_skipped() -> None:
    omni = FakeAdapter("omniroute", healthy=False)
    free = FakeAdapter("freellmapi")
    gateway = AIGateway([omni, free])

    response = gateway.complete(make_request())

    assert response.provider == "freellmapi"
    assert omni.calls == 0
    assert free.calls == 1


def test_preferred_provider_overrides_default_order(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AI_GATEWAY_ORDER", "omniroute,freellmapi")
    omni = FakeAdapter("omniroute")
    free = FakeAdapter("freellmapi")
    gateway = AIGateway([omni, free])

    response = gateway.complete(make_request(), preferred="freellmapi")

    assert response.provider == "freellmapi"
    assert free.calls == 1
    assert omni.calls == 0


def test_all_gateways_failed_returns_controlled_error() -> None:
    omni = FakeAdapter("omniroute", failure=True)
    free = FakeAdapter("freellmapi", failure=True)
    gateway = AIGateway([omni, free])

    with pytest.raises(AIProviderError, match="هیچ Gateway قابل استفاده‌ای"):
        gateway.complete(make_request())


def test_probe_reports_real_gateway_reachability() -> None:
    omni = FakeAdapter("omniroute", probe_ok=True)
    free = FakeAdapter("freellmapi", probe_ok=False)
    gateway = AIGateway([omni, free])

    status = gateway.probe()

    assert status == {"omniroute": True, "freellmapi": False}
    assert omni.probe_calls == 1
    assert free.probe_calls == 1
