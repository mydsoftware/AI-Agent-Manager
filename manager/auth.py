from __future__ import annotations

import hashlib
import hmac
import os


class APIAuthenticator:
    """احراز هویت ساده برای API با استفاده از کلید محیطی."""

    def __init__(self, environment_name: str = "AI_AGENT_MANAGER_API_KEY") -> None:
        self.environment_name = environment_name
        self.api_key = os.getenv(environment_name)

    @property
    def enabled(self) -> bool:
        return bool(os.getenv(self.environment_name) or self.api_key)

    def validate(self, provided_key: str | None) -> bool:
        """کلید را در زمان درخواست از محیط می‌خواند تا تست و runtime هر دو درست باشند."""
        configured_key = os.getenv(self.environment_name) or self.api_key
        if not configured_key or not provided_key:
            return False
        expected = hashlib.sha256(configured_key.encode("utf-8")).digest()
        provided = hashlib.sha256(provided_key.encode("utf-8")).digest()
        return hmac.compare_digest(expected, provided)
