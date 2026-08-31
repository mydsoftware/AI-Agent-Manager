"""Provider Freebuff - ارائه‌دهنده مستقل."""

from __future__ import annotations

from ..config import ProviderConfig
from ..openai_compatible import OpenAICompatibleAdapter


class FreebuffProvider(OpenAICompatibleAdapter):
    """Adapter Freebuff - اگر OpenAI-compatible باشد از Adapter مشترک استفاده می‌کند."""

    def __init__(self, config: ProviderConfig | None = None) -> None:
        import os

        if config is None:
            config = ProviderConfig(
                name="freebuff",
                base_url=os.getenv("FREEBUFF_BASE_URL", ""),
                api_key=os.getenv("FREEBUFF_API_KEY", ""),
                model=os.getenv("FREEBUFF_MODEL", ""),
            )

        super().__init__(
            name=config.name,
            base_url=config.base_url,
            api_key=config.api_key,
            timeout=config.timeout,
        )
        self.default_model = config.model
