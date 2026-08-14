from agents.registry import create_default_registry
from manager.task import Task
from manager.task_router import IntelligentTaskRouter


def test_github_task_is_routed_to_github_project():
    router = IntelligentTaskRouter(create_default_registry())
    task = Task(id="1", agent="", description="برای repository یک branch و Pull Request بساز")
    decision = router.select(task)
    assert decision.agent == "github-project"


def test_test_task_is_routed_to_qa():
    router = IntelligentTaskRouter(create_default_registry())
    task = Task(id="2", agent="", description="pytest را اجرا و خطاهای تست را بررسی کن")
    decision = router.select(task)
    assert decision.agent == "qa"


def test_explicit_agent_has_priority():
    router = IntelligentTaskRouter(create_default_registry())
    task = Task(id="3", agent="developer", description="repository را بررسی کن")
    decision = router.select(task)
    assert decision.agent == "developer"
