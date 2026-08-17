"""تست‌های Integration واقعی برای OmniRoute و FreeLLMAPI.

این تست‌ها فقط وقتی اجرا می‌شوند که متغیرهای محیطی هر Gateway تنظیم شده باشند.
در CI معمولی skip می‌شوند و هیچ Secretی در repository ذخیره نمی‌شود.
"""

from __future__ import annotations

import os

import pytest

from ai_gateway import AIGateway, AIMessage, AIProviderError, AIRequest


def _configured(name: str) -> bool:
    return bool(os.getenv(f"{name}_BASE_URL") and os.getenv(f"{name}_API_KEY"))


@pytest.mark.integration
@pytest.mark.parametrize("provider", ["OMNIROUTE", "FREELLMAPI"])
def test_real_gateway_completion(provider: str) -> None:
    if not _configured(provider):
        pytest.skip(f"{provider} برای Integration Test تنظیم نشده است")

    gateway = AIGateway()
    model = os.getenv(f"{provider}_MODEL", os.getenv("AI_INTEGRATION_MODEL", "auto"))
    response = gateway.complete(
        AIRequest(
            messages=[AIMessage(role="user", content="پاسخ را فقط با کلمه OK بده.")],
            model=model,
            max_tokens=16,
            temperature=0,
        ),
        preferred=provider.lower(),
    )

    assert response.content.strip()
    assert response.provider == provider.lower()


@pytest.mark.integration
def test_real_failover_when_primary_is_unreachable(monkeypatch: pytest.MonkeyPatch) -> None:
    if not (_configured("OMNIROUTE") and _configured("FREELLMAPI")):
        pytest.skip("هر دو Gateway برای تست Failover واقعی باید تنظیم شده باشند")

    monkeypatch.setenv("OMNIROUTE_BASE_URL", "http://127.0.0.1:1/v1")
    gateway = AIGateway()
    model = os.getenv("FREELLMAPI_MODEL", os.getenv("AI_INTEGRATION_MODEL", "auto"))

    response = gateway.complete(
        AIRequest(
            messages=[AIMessage(role="user", content="پاسخ را فقط با کلمه OK بده.")],
            model=model,
            max_tokens=16,
            temperature=0,
        ),
        preferred="omniroute",
    )

    assert response.content.strip()
    assert response.provider == "freellmapi"
