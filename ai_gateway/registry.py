"""ثبت و مدیریت Providerهای AI."""

from __future__ import annotations

from .config import GatewayConfig, ProviderConfig
from .models import AIProviderAdapter


class ProviderRegistry:
    """ثبت مرکزی Providerها برای کشف و مدیریت."""

    def __init__(self, config: GatewayConfig | None = None) -> None:
        self.config = config or GatewayConfig.from_environment()
        self._adapters: dict[str, AIProviderAdapter] = {}
        self._health_cache: dict[str, bool] = {}
        self._error_counts: dict[str, int] = {}

    def register(self, adapter: AIProviderAdapter) -> None:
        """یک Adapter جدید را ثبت می‌کند."""
        self._adapters[adapter.name] = adapter
        self._health_cache[adapter.name] = True
        self._error_counts[adapter.name] = 0

    def get(self, name: str) -> AIProviderAdapter | None:
        """Adapter با نام مشخص را برمی‌گرداند."""
        return self._adapters.get(name)

    def list_providers(self) -> list[str]:
        """نام تمام Providerهای ثبت‌شده را برمی‌گرداند."""
        return sorted(self._adapters.keys())

    def list_enabled(self) -> list[str]:
        """نام Providerهای فعال و سالم را برمی‌گرداند."""
        return [
            name for name, adapter in self._adapters.items()
            if self._health_cache.get(name, False)
        ]

    def mark_healthy(self, name: str) -> None:
        """ وضعیت سلامت Provider را ثبت می‌کند."""
        self._health_cache[name] = True
        self._error_counts[name] = 0

    def mark_unhealthy(self, name: str) -> None:
        """وضعیت عدم سلامت Provider را ثبت می‌کند."""
        self._health_cache[name] = False
        self._error_counts[name] = self._error_counts.get(name, 0) + 1

    def record_error(self, name: str) -> None:
        """خطای Provider را ثبت می‌کند."""
        self._error_counts[name] = self._error_counts.get(name, 0) + 1
        if self._error_counts[name] >= 3:
            self._health_cache[name] = False

    def get_error_count(self, name: str) -> int:
        """تعداد خطاهای ثبت‌شده Provider را برمی‌گرداند."""
        return self._error_counts.get(name, 0)

    def reset_errors(self, name: str) -> None:
        """شمارنده خطای Provider را بازنشانی می‌کند."""
        self._error_counts[name] = 0
        self._health_cache[name] = True

    def health_status(self) -> dict[str, dict]:
        """وضعیت کامل سلامت تمام Providerها را برمی‌گرداند."""
        return {
            name: {
                "healthy": self._health_cache.get(name, False),
                "error_count": self._error_counts.get(name, 0),
                "has_adapter": name in self._adapters,
            }
            for name in self._adapters
        }
