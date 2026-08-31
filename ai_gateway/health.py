"""بررسی سلامت و مانیتورینگ Providerها."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .config import GatewayConfig
from .models import AIProviderAdapter
from .registry import ProviderRegistry


class HealthChecker:
    """بررسی سلامت Providerها."""

    def __init__(self, registry: ProviderRegistry, config: GatewayConfig | None = None) -> None:
        self.registry = registry
        self.config = config or GatewayConfig.from_environment()
        self._last_check: str | None = None
        self._results: dict[str, bool] = {}

    def check_all(self) -> dict[str, dict[str, Any]]:
        """سلامت تمام Providerها را بررسی می‌کند."""
        results: dict[str, dict[str, Any]] = {}

        for name, adapter in self.registry._adapters.items():
            health = {
                "configured": adapter.health(),
                "probe": False,
                "healthy": False,
            }

            if adapter.health():
                try:
                    probe_result = adapter.probe()
                    health["probe"] = probe_result
                    health["healthy"] = probe_result
                    if probe_result:
                        self.registry.mark_healthy(name)
                    else:
                        self.registry.mark_unhealthy(name)
                except Exception as exc:
                    health["healthy"] = False
                    self.registry.mark_unhealthy(name)
                    health["error"] = str(exc)
            else:
                health["healthy"] = False
                self.registry.mark_unhealthy(name)

            results[name] = health

        self._results = {k: v["healthy"] for k, v in results.items()}
        self._last_check = datetime.now(timezone.utc).isoformat()
        return results

    def check_one(self, name: str) -> dict[str, Any]:
        """سلامت یک Provider خاص را بررسی می‌کند."""
        adapter = self.registry.get(name)
        if adapter is None:
            return {"configured": False, "probe": False, "healthy": False, "error": "Provider ثبت نشده است."}

        health = {"configured": adapter.health(), "probe": False, "healthy": False}

        if adapter.health():
            try:
                probe_result = adapter.probe()
                health["probe"] = probe_result
                health["healthy"] = probe_result
                if probe_result:
                    self.registry.mark_healthy(name)
                else:
                    self.registry.mark_unhealthy(name)
            except Exception as exc:
                health["healthy"] = False
                self.registry.mark_unhealthy(name)
                health["error"] = str(exc)
        else:
            self.registry.mark_unhealthy(name)

        return health

    def summary(self) -> dict[str, Any]:
        """خلاصه وضعیت سلامت را برمی‌گرداند."""
        total = len(self.registry._adapters)
        healthy = sum(1 for v in self._results.values() if v)
        return {
            "total": total,
            "healthy": healthy,
            "unhealthy": total - healthy,
            "last_check": self._last_check,
            "providers": dict(self._results),
        }
