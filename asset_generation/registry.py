"""ثبت و مدیریت Providerهای تولید Asset."""

from __future__ import annotations

from typing import Any

from .base import AssetGenerator, AssetResult, AssetSpec


class AssetProviderRegistry:
    """ثبت مرکزی Providerهای تولید Asset."""

    def __init__(self) -> None:
        self._providers: dict[str, AssetGenerator] = {}

    def register(self, provider: AssetGenerator) -> None:
        """Provider جدیدی را ثبت می‌کند."""
        self._providers[provider.name] = provider

    def get(self, name: str) -> AssetGenerator | None:
        """Provider با نام مشخص را برمی‌گرداند."""
        return self._providers.get(name)

    def list_providers(self) -> list[str]:
        """فهرست Providerهای ثبت‌شده."""
        return sorted(self._providers.keys())

    def list_enabled(self) -> list[str]:
        """فهرست Providerهای فعال."""
        return [name for name, p in self._providers.items() if p.health()]

    def generate(self, spec: AssetSpec, output_dir: str, preferred: str | None = None) -> AssetResult:
        """Asset را با Provider مناسب تولید می‌کند."""
        if preferred:
            provider = self.get(preferred)
            if provider and provider.health():
                return provider.generate(spec, output_dir)

        for name in self.list_enabled():
            provider = self._providers[name]
            try:
                result = provider.generate(spec, output_dir)
                if result.success:
                    return result
            except Exception:
                continue

        return AssetResult(
            success=False,
            spec=spec,
            error="هیچ Provider تولید Asset در دسترس نیست.",
        )

    def health(self) -> dict[str, bool]:
        """وضعیت سلامت Providerها."""
        return {name: p.health() for name, p in self._providers.items()}
