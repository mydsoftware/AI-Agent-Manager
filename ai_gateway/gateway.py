from __future__ import annotations

import os
from collections.abc import Sequence

from .models import AIProviderAdapter, AIProviderError, AIRequest, AIResponse
from .openai_compatible import from_environment


class AIGateway:
    """لایه واحد AI-Agent-Manager با دو مسیر مستقل OmniRoute و FreeLLMAPI."""

    def __init__(self, adapters: Sequence[AIProviderAdapter] | None = None) -> None:
        if adapters is None:
            adapters = from_environment()
        self.adapters = {adapter.name: adapter for adapter in adapters}

    def _ordered(self, preferred: str | None) -> list[AIProviderAdapter]:
        configured = os.getenv("AI_GATEWAY_ORDER", "omniroute,freellmapi")
        names = [name.strip() for name in configured.split(",") if name.strip()]
        if preferred and preferred in self.adapters:
            names = [preferred] + [name for name in names if name != preferred]
        return [self.adapters[name] for name in names if name in self.adapters]

    def complete(self, request: AIRequest, preferred: str | None = None) -> AIResponse:
        """درخواست را ارسال می‌کند و فقط در صورت خطای واقعی به Gateway بعدی failover می‌کند."""
        errors: list[str] = []
        for adapter in self._ordered(preferred):
            if not adapter.health():
                errors.append(f"{adapter.name}: تنظیم نشده")
                continue
            try:
                return adapter.complete(request)
            except AIProviderError as exc:
                errors.append(str(exc))

        raise AIProviderError("هیچ Gateway قابل استفاده‌ای پاسخ نداد: " + " | ".join(errors))

    def health(self) -> dict[str, bool]:
        """وضعیت پیکربندی را بدون تماس شبکه گزارش می‌کند."""
        return {name: adapter.health() for name, adapter in self.adapters.items()}

    def probe(self) -> dict[str, bool]:
        """سلامت واقعی Gatewayها را با endpoint /models بررسی می‌کند."""
        return {name: adapter.probe() for name, adapter in self.adapters.items()}
