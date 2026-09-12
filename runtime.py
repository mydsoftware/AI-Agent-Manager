from __future__ import annotations

from agents.developer_agent import DeveloperAgent
from agents.research_agent import ResearchAgent
from agents.registry import create_default_registry
from agents.registry_manager import AgentRegistryManager
from agents.registry_store import AgentRegistryStore
from manager.agent_governance import AgentGovernance
from manager.agent_team import AgentTeam
from manager.executor import TaskExecutor
from manager.llm_gateway import LLMGateway
from manager.loop import AgenticLoop
from manager.memory import Memory
from manager.model_router import ModelRouter
from manager.orchestrator import ManagerOrchestrator
from manager.persistent_memory import PersistentMemory
from manager.report import ManagerReport
from manager.router import Router
from manager.task import Task


class ManagerRuntime:
    """محیط اجرای اصلی مدیر چندایجنتی با LLM محلی اختیاری."""

    def __init__(self, database_path: str = "data/manager.db", registry_path: str = "data/agents.json") -> None:
        self.registry = create_default_registry()
        self.llm = LLMGateway()
        self.model_router = ModelRouter()
        self.registry.register_instance(DeveloperAgent(self.llm, self.model_router))
        self.registry.register_instance(ResearchAgent(self.llm, self.model_router))
        self.registry_manager = AgentRegistryManager(self.registry)
        self.registry_store = AgentRegistryStore(registry_path)
        self.agent_team = AgentTeam(self.registry_manager, self.registry_store)
        self.governance = AgentGovernance(self.registry_manager)
        self.router = Router(self.registry, self.governance)
        self.memory = Memory()
        self.persistent_memory = PersistentMemory(database_path)
        self.loop = AgenticLoop(self.router, self.memory)
        self.executor = TaskExecutor(self.loop)
        self.orchestrator = ManagerOrchestrator(memory=self.memory)

    def run(self, request: str, agent: str = "developer") -> ManagerReport:
        """درخواست کاربر را از تحلیل نیت تا گزارش نهایی اجرا می‌کند."""
        self.persistent_memory.add("شروع درخواست", {"request": request, "agent": agent})
        report = self.orchestrator.execute(request, self.executor, agent)
        self.persistent_memory.add("پایان درخواست", report.to_dict())
        self.persistent_memory.add("LLM Gateway Stats", self.llm.stats)
        return report

    def run_tasks(self, tasks: list[Task]) -> ManagerReport:
        """مجموعه‌ای از وظایف آماده را اجرا، ثبت و گزارش می‌کند."""
        try:
            self.executor.run(tasks)
        except Exception as error:
            self.persistent_memory.add("خطای اجرای وظایف", str(error))
        report = ManagerReport(tasks)
        self.persistent_memory.add("LLM Gateway Stats", self.llm.stats)
        self.persistent_memory.add("پایان اجرای وظایف", report.to_dict())
        return report


if __name__ == "__main__":
    runtime = ManagerRuntime()
    report = runtime.run("بررسی اولیه سیستم مدیریت ایجنت‌ها")
    print(report.to_dict())
