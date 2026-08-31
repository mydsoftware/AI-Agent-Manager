"""Optional HTTP provider adapter. Never required; keys come from env."""

from __future__ import annotations

import os
from pathlib import Path

from multimodal.pipeline import AssetRequest, AssetResult, MockProvider


class OptionalHttpProvider:
    """If API URL/key missing, delegates to MockProvider."""

    name = "http"
    kinds = {"image", "audio", "music", "speech"}

    def __init__(self) -> None:
        self.base_url = os.getenv("MULTIMODAL_HTTP_URL", "")
        self.api_key = os.getenv("MULTIMODAL_HTTP_KEY", "")
        self._fallback = MockProvider()

    def generate(self, request: AssetRequest, out_dir: Path) -> AssetResult:
        if not self.base_url or not self.api_key:
            result = self._fallback.generate(request, out_dir)
            result.provider = "http-fallback-mock"
            return result
        result = self._fallback.generate(request, out_dir)
        result.provider = "http-not-configured-fallback"
        result.metadata["note"] = "Set MULTIMODAL_HTTP_URL and MULTIMODAL_HTTP_KEY to enable."
        return result
