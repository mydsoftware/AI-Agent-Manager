from __future__ import annotations

import os


class ModelRouter:
    """انتخاب مدل محلی بر اساس نقش Agent و قابلیت موردنیاز."""

    DEFAULTS = {
        "planner": "qwen3.5-9b",
        "developer": "qwen3.5-9b",
        "coder": "qwen2.5-coder-7b",
        "researcher": "qwen3.5-9b",
        "reviewer": "qwen2.5-coder-7b",
        "tester": "qwen2.5-coder-7b",
        "vision": "qwen3-vl-4b-instruct",
        "embedding": "text-embedding-nomic-embed-text-v1.5",
    }

    ENV_NAMES = {
        "planner": "LLM_MODEL_PLANNER",
        "developer": "LLM_MODEL_DEVELOPER",
        "coder": "LLM_MODEL_CODER",
        "researcher": "LLM_MODEL_RESEARCHER",
        "reviewer": "LLM_MODEL_REVIEWER",
        "tester": "LLM_MODEL_TESTER",
        "vision": "LLM_MODEL_VISION",
        "embedding": "LLM_MODEL_EMBEDDING",
    }

    def __init__(self, overrides: dict[str, str] | None = None) -> None:
        self.overrides = overrides or {}

    def resolve(self, role: str, *, capability: str | None = None) -> str:
        key = capability or role
        if key in self.overrides:
            return self.overrides[key]
        env_name = self.ENV_NAMES.get(key)
        if env_name and os.getenv(env_name):
            return os.environ[env_name]
        if key in self.DEFAULTS:
            return self.DEFAULTS[key]
        return os.getenv("LLM_MODEL", self.DEFAULTS["developer"])
