from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class AIMessage:
    """یک پیام استاندارد مستقل از Provider."""

    role: str
    content: str


@dataclass
class AIRequest:
    """درخواست استانداردی که Adapterها دریافت می‌کنند."""

    messages: list[AIMessage]
    model: str = "auto"
    temperature: float | None = None
    max_tokens: int | None = None
    tools: list[dict[str, Any]] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AIResponse:
    """پاسخ نرمال‌شده از هر Gateway."""

    content: str
    provider: str
    model: str
    raw: dict[str, Any] = field(default_factory=dict)
    usage: dict[str, Any] = field(default_factory=dict)


class AIProviderError(RuntimeError):
    """خطای ارتباط یا پاسخ نامعتبر از Provider/Gateway."""


class AIProviderAdapter:
    """قرارداد مشترک OmniRoute و FreeLLMAPI."""

    name: str

    def complete(self, request: AIRequest) -> AIResponse:
        raise NotImplementedError

    def health(self) -> bool:
        """بررسی سریع پیکربندی محلی؛ بدون تماس شبکه."""
        raise NotImplementedError

    def probe(self) -> bool:
        """بررسی واقعی دسترسی به Gateway؛ برای Integration/Observability."""
        raise NotImplementedError
