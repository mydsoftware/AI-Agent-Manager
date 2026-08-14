from agents.registry import create_default_registry
from manager.task import Task
from manager.task_router import IntelligentTaskRouter


def test_github_task_enables_engineering():
    router = IntelligentTaskRouter(create_default_registry())
    decision = router.select(Task(id="1", agent="", description="یک Pull Request در GitHub بساز"))
    assert decision.agent == "github-project"
    assert decision.engineering is True


def test_research_task_does_not_enable_engineering():
    router = IntelligentTaskRouter(create_default_registry())
    decision = router.select(Task(id="2", agent="", description="تحلیل معماری سیستم"))
    assert decision.agent == "research"
    assert decision.engineering is False
