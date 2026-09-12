from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


class LLMError(RuntimeError):
    """خطای ارتباط یا پاسخ نامعتبر از LLM."""


@dataclass(frozen=True)
class LLMResponse:
    content: str
    model: str
    provider: str
    latency_ms: int
    usage: dict[str, Any]


class LLMGateway:
    """Gateway سبک و بدون وابستگی برای APIهای OpenAI-compatible."""

    def __init__(self, base_url: str | None = None, api_key: str | None = None, provider: str | None = None, timeout: float | None = None, max_retries: int | None = None) -> None:
        self.base_url = (base_url or os.getenv("LLM_BASE_URL", "http://127.0.0.1:1234/v1")).rstrip("/")
        self.api_key = api_key or os.getenv("LLM_API_KEY", "lm-studio")
        self.provider = provider or os.getenv("LLM_PROVIDER", "lmstudio")
        self.timeout = timeout if timeout is not None else float(os.getenv("LLM_TIMEOUT", "120"))
        self.max_retries = max(0, max_retries if max_retries is not None else int(os.getenv("LLM_MAX_RETRIES", "2")))
        self.stats: dict[str, int] = {"requests": 0, "success": 0, "failures": 0, "retries": 0, "context_reductions": 0}

    def complete(self, messages: list[dict[str, Any]], model: str, *, temperature: float = 0.2, max_tokens: int | None = None) -> LLMResponse:
        if not model:
            raise LLMError("مدل LLM مشخص نشده است.")
        current_messages = list(messages)
        url = f"{self.base_url}/chat/completions"
        last_error: Exception | None = None

        for attempt in range(self.max_retries + 1):
            payload: dict[str, Any] = {"model": model, "messages": current_messages, "temperature": temperature}
            if max_tokens is not None:
                payload["max_tokens"] = max_tokens
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            self.stats["requests"] += 1
            started = time.perf_counter()
            try:
                request = urllib.request.Request(url, data=body, headers=headers, method="POST")
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    data = json.loads(response.read().decode("utf-8"))
                content = self._extract_content(data)
                self.stats["success"] += 1
                return LLMResponse(content=content, model=str(data.get("model") or model), provider=self.provider, latency_ms=int((time.perf_counter() - started) * 1000), usage=data.get("usage") or {})
            except urllib.error.HTTPError as exc:
                error_body = exc.read().decode("utf-8", errors="ignore")
                last_error = LLMError(f"HTTP {exc.code}: {error_body[:500]}")
                if self._is_context_error(error_body) and len(current_messages) > 1:
                    current_messages = self._reduce_context(current_messages)
                    self.stats["context_reductions"] += 1
                    self.stats["retries"] += 1
                    continue
                if attempt < self.max_retries:
                    self.stats["retries"] += 1
                    time.sleep(min(2**attempt, 4))
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, LLMError) as exc:
                last_error = exc
                if attempt < self.max_retries:
                    self.stats["retries"] += 1
                    time.sleep(min(2**attempt, 4))

        self.stats["failures"] += 1
        raise LLMError(f"LLM request failed: {last_error}") from last_error

    @staticmethod
    def _is_context_error(text: str) -> bool:
        normalized = text.lower()
        return any(token in normalized for token in ("context length", "context window", "maximum context", "too many tokens", "exceeds available context"))

    @staticmethod
    def _reduce_context(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if len(messages) <= 2:
            reduced = list(messages)
            if len(reduced) == 2 and isinstance(reduced[1].get("content"), str):
                reduced[1] = {**reduced[1], "content": reduced[1]["content"][-12000:]}
            return reduced
        return [messages[0], *messages[-3:]]

    @staticmethod
    def _extract_content(data: dict[str, Any]) -> str:
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMError("پاسخ LLM ساختار معتبر chat completion ندارد.") from exc
        if not isinstance(content, str):
            raise LLMError("محتوای پاسخ LLM متنی نیست.")
        return content.strip()

    def health(self) -> bool:
        try:
            request = urllib.request.Request(f"{self.base_url}/models", headers={"Authorization": f"Bearer {self.api_key}"})
            with urllib.request.urlopen(request, timeout=min(self.timeout, 5)) as response:
                return 200 <= response.status < 300
        except Exception:
            return False
