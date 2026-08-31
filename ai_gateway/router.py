"""مسیریابی هوشمند مدل بر اساس نقش Agent."""

from __future__ import annotations

from .config import GatewayConfig
from .models import AIProviderAdapter, AIProviderError, AIRequest, AIResponse
from .registry import ProviderRegistry


class ModelRouter:
    """انتخاب مدل و Provider مناسب برای هر نقش Agent."""

    def __init__(self, registry: ProviderRegistry, config: GatewayConfig | None = None) -> None:
        self.registry = registry
        self.config = config or GatewayConfig.from_environment()

    def select_provider(self, agent_role: str | None = None) -> AIProviderAdapter | None:
        """Provider مناسب را برای نقش Agent انتخاب می‌کند."""
        enabled = self.config.get_enabled_providers()

        for provider_config in enabled:
            adapter = self.registry.get(provider_config.name)
            if adapter and self.registry._health_cache.get(provider_config.name, False):
                return adapter

        return None

    def select_model(self, agent_role: str | None = None, provider: AIProviderAdapter | None = None) -> str:
        """مدل مناسب را برای نقش Agent انتخاب می‌کند."""
        if agent_role and agent_role in self.config.models:
            return self.config.models[agent_role]

        if provider:
            provider_config = self.config.providers.get(provider.name)
            if provider_config:
                return provider_config.model

        return ""

    def route(self, request: AIRequest, agent_role: str | None = None) -> AIResponse:
        """درخواست را با مدل و Provider مناسب ارسال می‌کند."""
        adapter = self.select_provider(agent_role)
        if adapter is None:
            raise AIProviderError("هیچ Provider فعالی برای ارسال درخواست وجود ندارد.")

        model = self.select_model(agent_role, adapter)
        if model and request.model in ("auto", ""):
            request.model = model

        try:
            response = adapter.complete(request)
            self.registry.mark_healthy(adapter.name)
            return response
        except AIProviderError:
            self.registry.record_error(adapter.name)
            raise

    def list_available_models(self) -> dict[str, list[str]]:
        """فهرست مدل‌های موجود در هر Provider را برمی‌گرداند."""
        result: dict[str, list[str]] = {}
        for name in self.registry.list_enabled():
            adapter = self.registry.get(name)
            if adapter:
                provider_config = self.config.providers.get(name)
                default_model = provider_config.model if provider_config else ""
                result[name] = [default_model] if default_model else []
        return result
