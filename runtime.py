from __future__ import annotations

from agents.custom_agent import build_custom_agent
from agents.registry import create_default_registry
from agents.registry_manager import AgentRegistryManager
from agents.registry_store import AgentRegistryStore
from manager.agent_governance import AgentGovernance
from manager.agent_team import AgentTeam
from manager.executor import TaskExecutor
from manager.loop import AgenticLoop
from manager.memory import Memory
from manager.orchestrator import ManagerOrchestrator
from manager.persistent_memory import PersistentMemory
from manager.report import ManagerReport
from manager.router import Router
from manager.task import Task
from services.agent_deployment_adapter import AgentDeploymentAdapter
from services.agent_store import AgentStore


class ManagerRuntime:
    """محیط اجرای اصلی مدیر چندایجنتی با تیم Agent پایدار."""

    def __init__(self, database_path: str = "data/manager.db", registry_path: str = "data/agents.json") -> None:
        self.registry = create_default_registry()
        self.registry_manager = AgentRegistryManager(self.registry)
        self.registry_store = AgentRegistryStore(registry_path)
        self.agent_store = AgentStore(database_path)
        self._load_custom_agents()
        self.registry_store.load(self.registry_manager)
        self.agent_team = AgentTeam(self.registry_manager, self.registry_store)
        self.governance = AgentGovernance(self.registry_manager)
        self.router = Router(self.registry, self.governance)
        self.memory = Memory()
        self.persistent_memory = PersistentMemory(database_path)
        self.loop = AgenticLoop(self.router, self.memory)
        self.executor = TaskExecutor(self.loop)
        self.deployment_adapter = AgentDeploymentAdapter.from_task_executor(self.executor)
        self.orchestrator = ManagerOrchestrator(memory=self.memory)

    def _load_custom_agents(self) -> None:
        """ایجنت‌های سفارشی ذخیره‌شده را بدون اجرای کد دلخواه ثبت می‌کند."""
        for record in self.agent_store.list():
            agent_class = build_custom_agent(
                str(record["name"]),
                str(record["description"]),
                str(record["system_prompt"]),
                [item for item in str(record["capabilities"]).split(",") if item],
            )
            self.registry_manager.register(agent_class, str(record["description"]))
            if not bool(record["enabled"]):
                self.registry_manager.disable(str(record["name"]))

    def create_custom_agent(self, name: str, description: str, system_prompt: str, capabilities: list[str]) -> dict[str, object]:
        """یک ایجنت سفارشی داده‌محور ایجاد و در Runtime ثبت می‌کند."""
        record = self.agent_store.create(name, description, system_prompt, capabilities)
        agent_class = build_custom_agent(name=str(record["name"]), description=description,
                                         system_prompt=system_prompt, capabilities=capabilities)
        self.registry_manager.register(agent_class, description)
        self.registry_store.save(self.registry_manager)
        return record

    def delete_custom_agent(self, name: str) -> bool:
        """ایجنت سفارشی را از ذخیره‌ساز و Registry حذف می‌کند."""
        deleted = self.agent_store.delete(name)
        if deleted and self.registry_manager.registry.has(name):
            self.registry_manager.remove(name)
            self.registry_store.save(self.registry_manager)
        return deleted

    def run(self, request: str, agent: str = "developer") -> ManagerReport:
        """درخواست کاربر را از تحلیل نیت تا گزارش نهایی اجرا می‌کند."""
        self.persistent_memory.add("شروع درخواست", {"request": request, "agent": agent})
        report = self.orchestrator.execute(request, self.executor, agent)
        self.persistent_memory.add("پایان درخواست", report.to_dict())
        return report

    def run_tasks(self, tasks: list[Task]) -> ManagerReport:
        """مجموعه‌ای از وظایف آماده را اجرا، ثبت و گزارش می‌کند."""
        try:
            self.executor.run(tasks)
        except Exception as error:
            self.persistent_memory.add("خطای اجرای وظایف", str(error))
        report = ManagerReport(tasks)
        self.persistent_memory.add("پایان اجرای وظایف", report.to_dict())
        return report


if __name__ == "__main__":
    runtime = ManagerRuntime()
    report = runtime.run("بررسی اولیه سیستم مدیریت ایجنت‌ها")
    print(report.to_dict())
