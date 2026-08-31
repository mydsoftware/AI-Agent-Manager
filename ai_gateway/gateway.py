"""هسته اصلی AI Gateway - لایه واحد ارتباط با Providerها."""

from __future__ import annotations

from collections.abc import Sequence
from typing import overload

from .config import GatewayConfig
from .fallback import ProviderFallback
from .health import HealthChecker
from .models import AIProviderAdapter, AIProviderError, AIRequest, AIResponse
from .registry import ProviderRegistry
from .retry import RetryPolicy


class AIGateway:
    """لایه واحد AI-Agent-Manager با Failover خودکار بین Providerها.

    Providerها:
    - OpenRouter (مدل‌های رایگان)
    - Freebuff (ارائه‌دهنده مستقل)
    - OpenCode (ادغام Coding)
    - Ollama (اجرای Local)
    - OmniRoute / FreeLLMAPI (سازگاری با نسخه قبلی)
    """

    @overload
    def __init__(self, adapters: Sequence[AIProviderAdapter]) -> None: ...
    @overload
    def __init__(self, config: GatewayConfig | None = None) -> None: ...

    def __init__(self, adapters_or_config: Sequence[AIProviderAdapter] | GatewayConfig | None = None) -> None:
        if adapters_or_config is None:
            # حالت پیش‌فرض: پیکربندی از محیط
            self.config = GatewayConfig.from_environment()
            self.registry = ProviderRegistry(self.config)
            self._register_providers()
            self._use_legacy = False
        elif isinstance(adapters_or_config, list):
            # حالت سازگاری با نسخه قبلی: لیست Adapterها
            self.config = GatewayConfig.from_environment()
            self.registry = ProviderRegistry(self.config)
            self._use_legacy = True
            for adapter in adapters_or_config:
                self.registry.register(adapter)
        else:
            # حالت جدید: GatewayConfig
            self.config = adapters_or_config
            self.registry = ProviderRegistry(self.config)
            self._register_providers()
            self._use_legacy = False

        self._fallback = ProviderFallback(self.registry, self.config)
        self._health_checker = HealthChecker(self.registry, self.config)

    def _register_providers(self) -> None:
        """تمام Providerها را بر اساس پیکربندی ثبت می‌کند."""
        from .providers import FreebuffProvider, OllamaProvider, OpenCodeProvider, OpenRouterProvider

        provider_map = {
            "openrouter": OpenRouterProvider,
            "freebuff": FreebuffProvider,
            "opencode": OpenCodeProvider,
            "ollama": OllamaProvider,
        }

        for name, provider_class in provider_map.items():
            provider_config = self.config.providers.get(name)
            if provider_config:
                self.registry.register(provider_class(provider_config))

        # Providerهای سازگاری با نسخه قبلی
        for name in ("omniroute", "freellmapi"):
            provider_config = self.config.providers.get(name)
            if provider_config and provider_config.enabled:
                from .openai_compatible import OpenAICompatibleAdapter
                self.registry.register(OpenAICompatibleAdapter(
                    name=provider_config.name,
                    base_url=provider_config.base_url,
                    api_key=provider_config.api_key,
                    timeout=provider_config.timeout,
                ))

    def _ordered(self, preferred: str | None = None) -> list[AIProviderAdapter]:
        """فهرست مرتب‌شده Adapterها را بر اساس اولویت برمی‌گرداند."""
        import os
        if self._use_legacy:
            # در حالت legacy از نظم اصلی Adapterها استفاده کن
            configured = os.getenv("AI_GATEWAY_ORDER", "")
            if configured:
                names = [name.strip() for name in configured.split(",") if name.strip()]
            else:
                # اگر AI_GATEWAY_ORDER تنظیم نشده، از ترتیب ثبت‌شده استفاده کن
                names = list(self.registry._adapters.keys())

            if preferred and preferred in self.registry._adapters:
                names = [preferred] + [name for name in names if name != preferred]

            result = []
            for name in names:
                adapter = self.registry.get(name)
                if adapter:
                    result.append(adapter)
            return result

        configured = self.config.provider_priority or ["openrouter", "freebuff", "opencode", "ollama"]
        names = list(configured)

        if preferred and preferred in self.registry._adapters:
            names = [preferred] + [name for name in names if name != preferred]

        result = []
        for name in names:
            adapter = self.registry.get(name)
            if adapter:
                result.append(adapter)
        return result

    def complete(self, request: AIRequest, preferred: str | None = None, agent_role: str | None = None) -> AIResponse:
        """درخواست را با Failover خودکار ارسال می‌کند."""
        if self._use_legacy:
            return self._complete_legacy(request, preferred)
        return self._fallback.complete(request, preferred, agent_role)

    def _complete_legacy(self, request: AIRequest, preferred: str | None = None) -> AIResponse:
        """مسیر قدیمی برای سازگاری با تست‌های موجود."""
        errors: list[str] = []
        for adapter in self._ordered(preferred):
            if not adapter.health():
                errors.append(f"{adapter.name}: تنظیم نشده")
                continue
            try:
                return adapter.complete(request)
            except AIProviderError as exc:
                errors.append(str(exc))

        raise AIProviderError("هیچ Gateway قابل استفاده‌ای پاسخ نداد: " + " | ".join(errors))

    def health(self) -> dict[str, bool]:
        """وضعیت پیکربندی Providerها را برمی‌گرداند."""
        if self._use_legacy:
            return {name: adapter.health() for name, adapter in self.registry._adapters.items()}
        return {name: info["healthy"] for name, info in self._fallback.health().items()}

    def probe(self) -> dict[str, bool]:
        """سلامت واقعی Providerها را با تماس شبکه بررسی می‌کند."""
        if self._use_legacy:
            return {name: adapter.probe() for name, adapter in self.registry._adapters.items()}
        results = self._health_checker.check_all()
        return {name: info.get("healthy", False) for name, info in results.items()}

    def check_health(self) -> dict:
        """بررسی کامل سلامت با جزئیات بیشتر."""
        return self._health_checker.check_all()

    def summary(self) -> dict:
        """خلاصه وضعیت سلامت."""
        return self._health_checker.summary()

    def list_providers(self) -> list[str]:
        """فهرست تمام Providerهای ثبت‌شده."""
        return self.registry.list_providers()

    def list_enabled(self) -> list[str]:
        """فهرست Providerهای فعال."""
        return self.registry.list_enabled()

    def route(self, request: AIRequest, agent_role: str | None = None) -> AIResponse:
        """درخواست را با مسیریابی هوشمند ارسال می‌کند."""
        from .router import ModelRouter
        router = ModelRouter(self.registry, self.config)
        return router.route(request, agent_role)
