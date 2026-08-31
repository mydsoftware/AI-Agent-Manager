"""تست‌های پیکربندی و Registry AI Gateway."""

from __future__ import annotations

import os

from ai_gateway.config import GatewayConfig, ProviderConfig
from ai_gateway.registry import ProviderRegistry
from ai_gateway.retry import RetryExecutor, RetryPolicy, is_retryable_error
from ai_gateway.models import AIProviderError


def test_config_from_environment_defaults() -> None:
    """پیکربندی پیش‌فرض از متغیرهای محیطی ساخته می‌شود."""
    config = GatewayConfig.from_environment()
    assert "openrouter" in config.providers
    assert "freebuff" in config.providers
    assert "opencode" in config.providers
    assert "ollama" in config.providers


def test_config_provider_priority() -> None:
    """اولویت Providerها از متغیر محیطی خوانده می‌شود."""
    config = GatewayConfig.from_environment()
    assert len(config.provider_priority) >= 4


def test_config_enabled_providers() -> None:
    """Providerهای فعال به ترتیب اولویت برمی‌گردند."""
    config = GatewayConfig.from_environment()
    enabled = config.get_enabled_providers()
    assert isinstance(enabled, list)


def test_provider_config_defaults() -> None:
    """مقادیر پیش‌فرض ProviderConfig معتبر است."""
    pc = ProviderConfig(name="test", base_url="http://localhost", api_key="key")
    assert pc.name == "test"
    assert pc.enabled is True
    assert pc.timeout == 90.0


def test_registry_register_and_get() -> None:
    """ثبت و بازیابی Provider."""
    from ai_gateway.models import AIProviderAdapter, AIRequest, AIResponse

    class FakeProvider(AIProviderAdapter):
        name = "fake"

        def complete(self, request: AIRequest) -> AIResponse:
            return AIResponse(content="ok", provider="fake", model="test")

        def health(self) -> bool:
            return True

        def probe(self) -> bool:
            return True

    registry = ProviderRegistry()
    provider = FakeProvider()
    registry.register(provider)

    assert registry.get("fake") is provider
    assert "fake" in registry.list_providers()
    assert "fake" in registry.list_enabled()


def test_registry_health_tracking() -> None:
    """ردیابی سلامت Provider."""
    registry = ProviderRegistry()
    registry.mark_healthy("test")
    assert registry._health_cache.get("test") is True

    registry.mark_unhealthy("test")
    assert registry._health_cache.get("test") is False

    registry.reset_errors("test")
    registry.record_error("test")
    registry.record_error("test")
    registry.record_error("test")
    assert registry.get_error_count("test") == 3


def test_retry_executor_success() -> None:
    """اجرای موفق در اولین تلاش."""
    executor = RetryExecutor(RetryPolicy(max_attempts=3))
    result = executor.execute(lambda: "success")
    assert result == "success"
    assert executor.attempt == 1


def test_retry_executor_retryable_error() -> None:
    """تلاش مجدد در صورت خطای قابل بازیابی."""
    call_count = 0

    def operation() -> str:
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise AIProviderError("timeout error")
        return "success"

    executor = RetryExecutor(RetryPolicy(max_attempts=3, base_delay=0.01))
    result = executor.execute(operation, is_retryable=is_retryable_error)
    assert result == "success"
    assert executor.attempt == 3


def test_retry_executor_non_retryable() -> None:
    """توقف در صورت خطای غیرقابل بازیابی."""
    def operation() -> str:
        raise ValueError("invalid input")

    executor = RetryExecutor(RetryPolicy(max_attempts=3, base_delay=0.01))
    try:
        executor.execute(operation, is_retryable=is_retryable_error)
        assert False, "باید خطا پرتاب شود"
    except ValueError:
        pass
    assert executor.attempt == 1


def test_is_retryable_error_network() -> None:
    """خطاهای شبکه قابل بازیابی هستند."""
    assert is_retryable_error(AIProviderError("timeout")) is True
    assert is_retryable_error(AIProviderError("connection refused")) is True
    assert is_retryable_error(AIProviderError("rate limit 429")) is True


def test_is_retryable_error_validation() -> None:
    """خطاهای اعتبارسنجی غیرقابل بازیابی هستند."""
    assert is_retryable_error(ValueError("bad input")) is False
    assert is_retryable_error(KeyError("missing")) is False
