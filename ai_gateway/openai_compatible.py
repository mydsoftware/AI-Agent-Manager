from __future__ import annotations

import json
import os
from urllib import error, request

from .models import AIMessage, AIProviderAdapter, AIProviderError, AIRequest, AIResponse


class OpenAICompatibleAdapter(AIProviderAdapter):
    """Adapter مشترک برای Gatewayهای سازگار با OpenAI Chat Completions."""

    def __init__(self, name: str, base_url: str, api_key: str, timeout: float = 90.0) -> None:
        self.name = name
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    def _payload(self, req: AIRequest) -> dict:
        payload = {
            "model": req.model,
            "messages": [{"role": m.role, "content": m.content} for m in req.messages],
        }
        if req.temperature is not None:
            payload["temperature"] = req.temperature
        if req.max_tokens is not None:
            payload["max_tokens"] = req.max_tokens
        if req.tools:
            payload["tools"] = req.tools
        return payload

    def complete(self, req: AIRequest) -> AIResponse:
        endpoint = f"{self.base_url}/chat/completions"
        body = json.dumps(self._payload(req), ensure_ascii=False).encode("utf-8")
        http_request = request.Request(
            endpoint,
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        try:
            with request.urlopen(http_request, timeout=self.timeout) as response:
                raw = json.loads(response.read().decode("utf-8"))
        except (error.URLError, error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
            raise AIProviderError(f"ارتباط با {self.name} ناموفق بود: {exc}") from exc

        try:
            choice = raw["choices"][0]
            message = choice["message"]
            content = message.get("content") or ""
        except (KeyError, IndexError, TypeError) as exc:
            raise AIProviderError(f"پاسخ {self.name} ساختار معتبر ندارد.") from exc

        return AIResponse(
            content=content,
            provider=self.name,
            model=raw.get("model", req.model),
            raw=raw,
            usage=raw.get("usage", {}),
        )

    def health(self) -> bool:
        return bool(self.base_url and self.api_key)


def from_environment() -> tuple[OpenAICompatibleAdapter, OpenAICompatibleAdapter]:
    """دو Gateway مستقل را از Environment می‌سازد؛ هیچ Providerی به دیگری وابسته نیست."""
    omni = OpenAICompatibleAdapter(
        "omniroute",
        os.getenv("OMNIROUTE_BASE_URL", "http://localhost:20128/v1"),
        os.getenv("OMNIROUTE_API_KEY", ""),
    )
    free = OpenAICompatibleAdapter(
        "freellmapi",
        os.getenv("FREELLMAPI_BASE_URL", "http://localhost:3001/v1"),
        os.getenv("FREELLMAPI_API_KEY", ""),
    )
    return omni, free
