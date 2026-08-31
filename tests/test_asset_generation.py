"""تست‌های سیستم تولید Asset."""

from __future__ import annotations

import tempfile

from asset_generation.base import AssetGenerator, AssetResult, AssetSpec
from asset_generation.registry import AssetProviderRegistry


class FakeAssetGenerator(AssetGenerator):
    """تولیدکننده Asset جعلی برای تست."""

    name = "fake"

    def generate(self, spec: AssetSpec, output_dir: str) -> AssetResult:
        return AssetResult(success=True, spec=spec, path=f"{output_dir}/{spec.filename or 'asset.png'}")

    def health(self) -> bool:
        return True


def test_asset_spec_defaults() -> None:
    """مقادیر پیش‌ypse AssetSpec."""
    spec = AssetSpec(id="a1", category="characters")
    assert spec.width == 512
    assert spec.height == 512
    assert spec.transparent is False


def test_asset_registry_register() -> None:
    """ثبت Provider."""
    registry = AssetProviderRegistry()
    registry.register(FakeAssetGenerator())
    assert "fake" in registry.list_providers()
    assert "fake" in registry.list_enabled()


def test_asset_registry_generate() -> None:
    """تولید Asset."""
    registry = AssetProviderRegistry()
    registry.register(FakeAssetGenerator())

    with tempfile.TemporaryDirectory() as tmpdir:
        spec = AssetSpec(id="a1", category="characters", filename="hero.png")
        result = registry.generate(spec, tmpdir)
        assert result.success is True


def test_asset_registry_no_providers() -> None:
    """عدم وجود Provider."""
    registry = AssetProviderRegistry()
    spec = AssetSpec(id="a1", category="characters")
    result = registry.generate(spec, "/tmp")
    assert result.success is False


def test_asset_registry_health() -> None:
    """وضعیت سلامت Providerها."""
    registry = AssetProviderRegistry()
    registry.register(FakeAssetGenerator())
    health = registry.health()
    assert health == {"fake": True}
