"""Provider OpenCode - ادغام Coding/Agent."""

from __future__ import annotations

from ..config import ProviderConfig
from ..openai_compatible import OpenAICompatibleAdapter


class OpenCodeProvider(OpenAICompatibleAdapter):
    """Adapter OpenCode - ادغام Adapter-based برای Coding."""

    def __init__(self, config: ProviderConfig | None = None) -> None:
        import os

        if config is None:
            config = ProviderConfig(
                name="opencode",
                base_url=os.getenv("OPENCODE_BASE_URL", ""),
                api_key=os.getenv("OPENCODE_API_KEY", ""),
                model=os.getenv("OPENCODE_MODEL", ""),
            )

        super().__init__(
            name=config.name,
            base_url=config.base_url,
            api_key=config.api_key,
            timeout=config.timeout,
        )
        self.default_model = config.model
