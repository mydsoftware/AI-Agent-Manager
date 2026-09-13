from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ContextResult:
    messages: list[dict[str, Any]]
    estimated_tokens: int
    compacted: bool


class ContextManager:
    """مدیریت بودجه context برای مدل‌های محلی با حافظه محدود."""

    def __init__(self, max_tokens: int = 12288, reserve_tokens: int = 1024) -> None:
        if max_tokens <= reserve_tokens:
            raise ValueError("max_tokens باید بزرگ‌تر از reserve_tokens باشد.")
        self.max_tokens = max_tokens
        self.reserve_tokens = reserve_tokens

    @staticmethod
    def estimate_tokens(messages: list[dict[str, Any]]) -> int:
        # تخمین محافظه‌کارانه و مستقل از tokenizer؛ برای routing کافی است.
        chars = sum(len(str(m.get("content", ""))) + 16 for m in messages)
        return max(1, (chars + 3) // 4)

    @staticmethod
    def _trim_message(message: dict[str, Any], max_tokens: int) -> dict[str, Any]:
        if max_tokens <= 0:
            return {**message, "content": ""}
        content = str(message.get("content", ""))
        max_chars = max(1, max_tokens * 4 - 16)
        if len(content) <= max_chars:
            return dict(message)
        return {**message, "content": content[:max_chars] + "\n[context truncated]"}

    def prepare(self, messages: list[dict[str, Any]]) -> ContextResult:
        budget = self.max_tokens - self.reserve_tokens
        estimated = self.estimate_tokens(messages)
        if estimated <= budget:
            return ContextResult(messages=list(messages), estimated_tokens=estimated, compacted=False)

        system = [m for m in messages if m.get("role") == "system"]
        rest = [m for m in messages if m.get("role") != "system"]
        kept: list[dict[str, Any]] = []
        used = 0

        for message in system:
            remaining = max(1, budget - used)
            trimmed = self._trim_message(message, remaining)
            cost = self.estimate_tokens([trimmed])
            if used + cost > budget:
                break
            kept.append(trimmed)
            used += cost

        kept_rest: list[dict[str, Any]] = []
        for message in reversed(rest):
            cost = self.estimate_tokens([message])
            if used + cost > budget:
                continue
            kept_rest.append(message)
            used += cost

        result = kept + list(reversed(kept_rest))
        return ContextResult(messages=result, estimated_tokens=self.estimate_tokens(result), compacted=True)
