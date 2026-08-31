"""Provider Ollama - اجرای Local."""

from __future__ import annotations

from ..config import ProviderConfig
from ..openai_compatible import OpenAICompatibleAdapter


class OllamaProvider(OpenAICompatibleAdapter):
    """Adapter Ollama برای اجرای Local بدون Cloud."""

    def __init__(self, config: ProviderConfig | None = None) -> None:
        import os

        if config is None:
            config = ProviderConfig(
                name="ollama",
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
                api_key=os.getenv("OLLAMA_API_KEY", "ollama"),
                model=os.getenv("OLLAMA_MODEL", ""),
                timeout=float(os.getenv("OLLAMA_TIMEOUT", "120")),
            )

        super().__init__(
            name=config.name,
            base_url=config.base_url,
            api_key=config.api_key,
            timeout=config.timeout,
        )
        self.default_model = config.model
