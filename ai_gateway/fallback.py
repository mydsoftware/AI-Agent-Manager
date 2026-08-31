"""سیستم Failover و انتخاب Provider جایگزین."""

from __future__ import annotations

from .config import GatewayConfig
from .models import AIProviderAdapter, AIProviderError, AIRequest, AIResponse
from .registry import ProviderRegistry
from .retry import RetryExecutor, RetryPolicy, is_retryable_error


class ProviderFallback:
    """ارسال درخواست با Failover خودکار بین Providerها."""

    def __init__(
        self,
        registry: ProviderRegistry,
        config: GatewayConfig | None = None,
        retry_policy: RetryPolicy | None = None,
    ) -> None:
        self.registry = registry
        self.config = config or GatewayConfig.from_environment()
        self.retry_policy = retry_policy or RetryPolicy(
            max_attempts=self.config.max_retries,
            base_delay=self.config.retry_base_delay,
            max_delay=self.config.retry_max_delay,
        )

    def _ordered_adapters(self, preferred: str | None = None) -> list[AIProviderAdapter]:
        """فهرست مرتب‌شده Adapterها را بر اساس اولویت و سلامت برمی‌گرداند."""
        adapters: list[AIProviderAdapter] = []

        # ابتدا Provider ترجیحی
        if preferred:
            adapter = self.registry.get(preferred)
            if adapter and self.registry._health_cache.get(preferred, True):
                adapters.append(adapter)

        # سپس بر اساس اولویت
        for name in self.config.provider_priority:
            if name == preferred:
                continue
            adapter = self.registry.get(name)
            if adapter and self.registry._health_cache.get(name, True):
                adapters.append(adapter)

        # سایر Providerهای ثبت‌شده که در اولویت نیستند
        for adapter in self.registry._adapters.values():
            if adapter not in adapters and self.registry._health_cache.get(adapter.name, True):
                adapters.append(adapter)

        return adapters

    def complete(
        self,
        request: AIRequest,
        preferred: str | None = None,
        agent_role: str | None = None,
    ) -> AIResponse:
        """درخواست را با Failover خودکار ارسال می‌کند."""
        errors: list[str] = []
        ordered = self._ordered_adapters(preferred)

        for adapter in ordered:
            # تنظیم مدل بر اساس نقش Agent
            if agent_role:
                resolved = self.config.resolve_model(agent_role, None)
                if resolved:
                    request.model = resolved

            executor = RetryExecutor(self.retry_policy)
            try:
                response = executor.execute(
                    lambda a=adapter: a.complete(request),
                    is_retryable=is_retryable_error,
                )
                self.registry.mark_healthy(adapter.name)
                return response
            except Exception as exc:
                errors.append(f"{adapter.name}: {exc}")
                self.registry.record_error(adapter.name)

        raise AIProviderError(
            "هیچ Provider قابل استفاده‌ای پاسخ نداد: " + " | ".join(errors)
        )

    def health(self) -> dict[str, dict]:
        """وضعیت سلامت و Retry همه Providerها را گزارش می‌کند."""
        status = self.registry.health_status()
        for name in status:
            status[name]["retry_count"] = self.registry.get_error_count(name)
        return status
