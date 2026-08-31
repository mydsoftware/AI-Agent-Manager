"""Feature flags and environment-backed settings for new platform modules."""

from __future__ import annotations

import os
from dataclasses import dataclass


def _bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    return int(raw)


def _float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    return float(raw)


@dataclass(frozen=True)
class Settings:
    memory_enabled: bool = True
    memory_backend: str = "sqlite"
    memory_path: str = "data/shared_memory.db"

    circuit_breaker_enabled: bool = True
    circuit_failure_threshold: int = 3
    circuit_recovery_seconds: float = 30.0
    max_task_retries: int = 5

    default_token_budget: int = 50_000
    default_cost_budget_usd: float = 1.0
    default_time_budget_seconds: float = 300.0
    daily_global_token_budget: int = 500_000
    daily_global_cost_budget_usd: float = 10.0

    sandbox_enabled: bool = True
    sandbox_backend: str = "subprocess"
    sandbox_timeout_seconds: float = 30.0
    sandbox_network: bool = False
    sandbox_allow_docker: bool = False

    hitl_enabled: bool = True
    hitl_expiry_seconds: float = 3600.0
    hitl_auto_approve_low: bool = True

    multimodal_enabled: bool = True
    multimodal_output_dir: str = "asset_generation/output"
    multimodal_default_provider: str = "mock"

    observability_enabled: bool = True
    observability_path: str = "data/traces.db"
    otel_enabled: bool = False

    plugins_enabled: bool = True
    plugins_dir: str = "plugins"

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            memory_enabled=_bool("MEMORY_ENABLED", True),
            memory_backend=os.getenv("MEMORY_BACKEND", "sqlite"),
            memory_path=os.getenv("MEMORY_PATH", "data/shared_memory.db"),
            circuit_breaker_enabled=_bool("CIRCUIT_BREAKER_ENABLED", True),
            circuit_failure_threshold=_int("CIRCUIT_FAILURE_THRESHOLD", 3),
            circuit_recovery_seconds=_float("CIRCUIT_RECOVERY_SECONDS", 30.0),
            max_task_retries=_int("MAX_TASK_RETRIES", 5),
            default_token_budget=_int("DEFAULT_TOKEN_BUDGET", 50_000),
            default_cost_budget_usd=_float("DEFAULT_COST_BUDGET_USD", 1.0),
            default_time_budget_seconds=_float("DEFAULT_TIME_BUDGET_SECONDS", 300.0),
            daily_global_token_budget=_int("DAILY_GLOBAL_TOKEN_BUDGET", 500_000),
            daily_global_cost_budget_usd=_float("DAILY_GLOBAL_COST_BUDGET_USD", 10.0),
            sandbox_enabled=_bool("SANDBOX_ENABLED", True),
            sandbox_backend=os.getenv("SANDBOX_BACKEND", "subprocess"),
            sandbox_timeout_seconds=_float("SANDBOX_TIMEOUT_SECONDS", 30.0),
            sandbox_network=_bool("SANDBOX_NETWORK", False),
            sandbox_allow_docker=_bool("SANDBOX_ALLOW_DOCKER", False),
            hitl_enabled=_bool("HITL_ENABLED", True),
            hitl_expiry_seconds=_float("HITL_EXPIRY_SECONDS", 3600.0),
            hitl_auto_approve_low=_bool("HITL_AUTO_APPROVE_LOW", True),
            multimodal_enabled=_bool("MULTIMODAL_ENABLED", True),
            multimodal_output_dir=os.getenv("MULTIMODAL_OUTPUT_DIR", "asset_generation/output"),
            multimodal_default_provider=os.getenv("MULTIMODAL_DEFAULT_PROVIDER", "mock"),
            observability_enabled=_bool("OBSERVABILITY_ENABLED", True),
            observability_path=os.getenv("OBSERVABILITY_PATH", "data/traces.db"),
            otel_enabled=_bool("OTEL_ENABLED", False),
            plugins_enabled=_bool("PLUGINS_ENABLED", True),
            plugins_dir=os.getenv("PLUGINS_DIR", "plugins"),
        )


def load_settings() -> Settings:
    return Settings.from_env()
