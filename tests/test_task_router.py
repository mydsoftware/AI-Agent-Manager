from agents.registry import create_default_registry
from manager.task import Task
from manager.task_router import IntelligentTaskRouter


def test_github_task_is_routed_to_github_project():
    router = IntelligentTaskRouter(create_default_registry())
    task = Task(id="1", title="کار GitHub", description="برای repository یک branch و Pull Request بساز", agent="")
    decision = router.select(task)
    assert decision.agent == "github-project"


def test_test_task_is_routed_to_qa():
    router = IntelligentTaskRouter(create_default_registry())
    task = Task(id="2", title="تست", description="pytest را اجرا و خطاهای تست را بررسی کن", agent="")
    decision = router.select(task)
    assert decision.agent == "qa"


def test_explicit_agent_has_priority():
    router = IntelligentTaskRouter(create_default_registry())
    task = Task(id="3", title="توسعه", description="repository را بررسی کن", agent="developer")
    decision = router.select(task)
    assert decision.agent == "developer"
