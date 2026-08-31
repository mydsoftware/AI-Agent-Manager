"""پیکربندی مرکزی AI Gateway."""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ProviderConfig:
    """تنظیمات یک Provider."""

    name: str
    base_url: str
    api_key: str
    model: str = ""
    timeout: float = 90.0
    enabled: bool = True
    priority: int = 100


@dataclass
class GatewayConfig:
    """پیکربندی کلی AI Gateway."""

    provider_priority: list[str] = field(default_factory=list)
    providers: dict[str, ProviderConfig] = field(default_factory=dict)
    max_retries: int = 3
    retry_base_delay: float = 1.0
    retry_max_delay: float = 30.0
    max_requests_per_execution: int = 100
    models: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_environment(cls) -> GatewayConfig:
        """پیکربندی را از متغیرهای محیطی می‌سازد."""
        priority_str = os.getenv("AI_PROVIDER_PRIORITY", "openrouter,freebuff,opencode,ollama")
        provider_priority = [p.strip() for p in priority_str.split(",") if p.strip()]

        providers: dict[str, ProviderConfig] = {}

        # OpenRouter
        providers["openrouter"] = ProviderConfig(
            name="openrouter",
            base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
            api_key=os.getenv("OPENROUTER_API_KEY", ""),
            model=os.getenv("OPENROUTER_MODEL", "openrouter/free"),
            timeout=float(os.getenv("OPENROUTER_TIMEOUT", "90")),
            enabled=bool(os.getenv("OPENROUTER_API_KEY")),
            priority=1,
        )

        # Freebuff
        providers["freebuff"] = ProviderConfig(
            name="freebuff",
            base_url=os.getenv("FREEBUFF_BASE_URL", ""),
            api_key=os.getenv("FREEBUFF_API_KEY", ""),
            model=os.getenv("FREEBUFF_MODEL", ""),
            timeout=float(os.getenv("FREEBUFF_TIMEOUT", "90")),
            enabled=bool(os.getenv("FREEBUFF_API_KEY") and os.getenv("FREEBUFF_BASE_URL")),
            priority=2,
        )

        # OpenCode
        providers["opencode"] = ProviderConfig(
            name="opencode",
            base_url=os.getenv("OPENCODE_BASE_URL", ""),
            api_key=os.getenv("OPENCODE_API_KEY", ""),
            model=os.getenv("OPENCODE_MODEL", ""),
            timeout=float(os.getenv("OPENCODE_TIMEOUT", "90")),
            enabled=bool(os.getenv("OPENCODE_API_KEY") and os.getenv("OPENCODE_BASE_URL")),
            priority=3,
        )

        # Ollama
        providers["ollama"] = ProviderConfig(
            name="ollama",
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
            api_key=os.getenv("OLLAMA_API_KEY", "ollama"),
            model=os.getenv("OLLAMA_MODEL", ""),
            timeout=float(os.getenv("OLLAMA_TIMEOUT", "120")),
            enabled=True,  # Ollama همیشه فعال است اگر نصب باشد
            priority=4,
        )

        # Legacy providers
        if os.getenv("OMNIROUTE_BASE_URL") and os.getenv("OMNIROUTE_API_KEY"):
            providers["omniroute"] = ProviderConfig(
                name="omniroute",
                base_url=os.getenv("OMNIROUTE_BASE_URL", "http://localhost:20128/v1"),
                api_key=os.getenv("OMNIROUTE_API_KEY", ""),
                model=os.getenv("OMNIROUTE_MODEL", ""),
                timeout=90.0,
                enabled=True,
                priority=5,
            )

        if os.getenv("FREELLMAPI_BASE_URL") and os.getenv("FREELLMAPI_API_KEY"):
            providers["freellmapi"] = ProviderConfig(
                name="freellmapi",
                base_url=os.getenv("FREELLMAPI_BASE_URL", "http://localhost:3001/v1"),
                api_key=os.getenv("FREELLMAPI_API_KEY", ""),
                model=os.getenv("FREELLMAPI_MODEL", ""),
                timeout=90.0,
                enabled=True,
                priority=6,
            )

        # Per-agent model routing
        models = {
            "planner": os.getenv("PLANNER_MODEL", ""),
            "developer": os.getenv("DEVELOPER_MODEL", ""),
            "reviewer": os.getenv("REVIEWER_MODEL", ""),
            "tester": os.getenv("TESTER_MODEL", ""),
            "researcher": os.getenv("RESEARCHER_MODEL", ""),
            "game_designer": os.getenv("GAME_DESIGNER_MODEL", ""),
            "game_developer": os.getenv("GAME_DEVELOPER_MODEL", ""),
        }

        return cls(
            provider_priority=provider_priority,
            providers=providers,
            max_retries=int(os.getenv("MAX_RETRIES", "3")),
            retry_base_delay=float(os.getenv("RETRY_BASE_DELAY", "1.0")),
            retry_max_delay=float(os.getenv("RETRY_MAX_DELAY", "30.0")),
            max_requests_per_execution=int(os.getenv("MAX_REQUESTS_PER_EXECUTION", "100")),
            models={k: v for k, v in models.items() if v},
        )

    def get_enabled_providers(self) -> list[ProviderConfig]:
        """فهرست Providerهای فعال را بر اساس اولویت برمی‌گرداند."""
        enabled = [p for p in self.providers.values() if p.enabled]
        priority_map = {name: i for i, name in enumerate(self.provider_priority)}
        enabled.sort(key=lambda p: priority_map.get(p.name, p.priority))
        return enabled

    def resolve_model(self, agent_role: str, provider: ProviderConfig | None = None) -> str:
        """مدل مناسب برای نقش Agent را انتخاب می‌کند."""
        if agent_role in self.models:
            return self.models[agent_role]
        if provider and provider.model:
            return provider.model
        return ""
