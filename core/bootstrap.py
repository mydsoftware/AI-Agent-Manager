"""Compose new subsystems for ManagerRuntime without breaking existing ctor."""

from __future__ import annotations

from dataclasses import dataclass

from config.settings import Settings, load_settings
from core.hitl.approvals import ApprovalGateway
from core.memory.context import ContextManager
from core.memory.store import SharedMemory, create_shared_memory
from core.observability.tracer import Tracer
from core.plugins.manager import PluginManager
from core.safety.budget import BudgetController
from core.safety.circuit_breaker import CircuitBreaker
from core.safety.sandbox import Sandbox
from multimodal.pipeline import AssetManager


@dataclass
class PlatformServices:
    settings: Settings
    memory: SharedMemory
    context: ContextManager
    budget: BudgetController
    sandbox: Sandbox
    approvals: ApprovalGateway
    tracer: Tracer
    plugins: PluginManager
    assets: AssetManager

    def breaker(self, name: str) -> CircuitBreaker:
        return CircuitBreaker(
            name=name,
            failure_threshold=self.settings.circuit_failure_threshold,
            recovery_seconds=self.settings.circuit_recovery_seconds,
        )


def build_services(settings: Settings | None = None) -> PlatformServices:
    settings = settings or load_settings()
    memory = create_shared_memory(settings.memory_path, settings.memory_backend)
    return PlatformServices(
        settings=settings,
        memory=memory,
        context=ContextManager(memory),
        budget=BudgetController(
            default_token_budget=settings.default_token_budget,
            default_cost_budget_usd=settings.default_cost_budget_usd,
            default_time_budget_seconds=settings.default_time_budget_seconds,
            daily_token_budget=settings.daily_global_token_budget,
            daily_cost_budget_usd=settings.daily_global_cost_budget_usd,
        ),
        sandbox=Sandbox(
            backend=settings.sandbox_backend,
            timeout_seconds=settings.sandbox_timeout_seconds,
            network=settings.sandbox_network,
            allow_docker=settings.sandbox_allow_docker,
        ),
        approvals=ApprovalGateway(
            expiry_seconds=settings.hitl_expiry_seconds,
            auto_approve_low=settings.hitl_auto_approve_low,
        ),
        tracer=Tracer(settings.observability_path),
        plugins=PluginManager(settings.plugins_dir),
        assets=AssetManager(settings.multimodal_output_dir, settings.multimodal_default_provider),
    )
