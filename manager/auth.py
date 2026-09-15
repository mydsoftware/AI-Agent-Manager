from __future__ import annotations

import hashlib
import hmac
import os


class APIAuthenticator:
    """احراز هویت API با استفاده از کلید محیطی."""

    def __init__(self, environment_name: str = "AI_AGENT_MANAGER_API_KEY") -> None:
        self.environment_name = environment_name
        self.api_key = os.getenv(environment_name)

    @property
    def enabled(self) -> bool:
        """مشخص می‌کند که کلید API تنظیم شده است یا خیر."""
        return bool(self.api_key)

    def validate(self, provided_key: str | None) -> bool:
        """کلید دریافتی را با مقایسه ثابت‌زمان بررسی می‌کند."""
        if not self.api_key or not provided_key:
            return False
        expected = hashlib.sha256(self.api_key.encode("utf-8")).digest()
        provided = hashlib.sha256(provided_key.encode("utf-8")).digest()
        return hmac.compare_digest(expected, provided)

    def extract_key(self, api_key_header: str | None, authorization_header: str | None) -> str | None:
        """کلید را از X-API-Key یا Authorization: Bearer استخراج می‌کند.

        X-API-Key برای سازگاری قبلی اولویت دارد. هدر Authorization فقط
        زمانی به‌عنوان کلید استفاده می‌شود که scheme آن دقیقاً Bearer باشد.
        """
        if api_key_header:
            return api_key_header.strip() or None
        if not authorization_header:
            return None
        scheme, separator, credentials = authorization_header.partition(" ")
        if separator and scheme.lower() == "bearer":
            return credentials.strip() or None
        return None
