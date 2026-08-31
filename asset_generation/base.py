"""کلاس پایه تولید Asset."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AssetSpec:
    """مشخصات یک Asset تصویری."""

    id: str
    category: str
    prompt: str = ""
    style: str = "pixel_art"
    width: int = 512
    height: int = 512
    transparent: bool = False
    filename: str = ""
    usage: str = ""


@dataclass
class AssetResult:
    """نتیجه تولید Asset."""

    success: bool
    spec: AssetSpec
    path: str = ""
    error: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class AssetGenerator(ABC):
    """قرارداد مشترک تولیدکننده‌های Asset."""

    name: str = "base"

    @abstractmethod
    def generate(self, spec: AssetSpec, output_dir: str) -> AssetResult:
        """Asset را تولید می‌کند."""
        raise NotImplementedError

    def health(self) -> bool:
        """وضعیت سلامت Provider."""
        return True
