"""Provider OpenRouter - پشتیبانی از مدل‌های رایگان."""

from __future__ import annotations

from ..config import ProviderConfig
from ..openai_compatible import OpenAICompatibleAdapter


class OpenRouterProvider(OpenAICompatibleAdapter):
    """Adapter OpenRouter با پشتیبانی از مدل‌های رایگان."""

    def __init__(self, config: ProviderConfig | None = None) -> None:
        import os

        if config is None:
            config = ProviderConfig(
                name="openrouter",
                base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
                api_key=os.getenv("OPENROUTER_API_KEY", ""),
                model=os.getenv("OPENROUTER_MODEL", "openrouter/free"),
            )

        super().__init__(
            name=config.name,
            base_url=config.base_url,
            api_key=config.api_key,
            timeout=config.timeout,
        )
        self.default_model = config.model

    def _get_headers(self) -> dict[str, str]:
        """هدرهای OpenRouter را با HTTP-Referer اضافه می‌کند."""
        headers = super()._headers()
        headers["HTTP-Referer"] = "https://github.com/mydsoftware/AI-Agent-Manager"
        headers["X-Title"] = "AI-Agent-Manager"
        return headers
