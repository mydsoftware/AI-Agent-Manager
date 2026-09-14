from manager.intention import UserIntent
from manager.multi_plan import MultiAgentPlanner


def test_vision_plan_uses_developer_with_vision_capability() -> None:
    plan = MultiAgentPlanner().plan(UserIntent(goal="این اسکرین‌شات را بررسی کن", agent=None))
    assert len(plan.tasks) == 1
    assert plan.tasks[0].agent == "developer"
    assert plan.tasks[0].capability == "vision"


def test_code_plan_preflights_repository_then_uses_coder() -> None:
    plan = MultiAgentPlanner().plan(UserIntent(goal="این کد را اصلاح کن", agent=None))
    assert plan.tasks[0].agent == "github"
    assert plan.tasks[0].title == "بررسی اولیه Repository"
    assert plan.tasks[1].agent == "developer"
    assert plan.tasks[1].capability == "coder"
    assert plan.tasks[1].depends_on == [plan.tasks[0].id]


def test_research_plan_uses_research_agent() -> None:
    plan = MultiAgentPlanner().plan(UserIntent(goal="تحقیق درباره معماری سیستم", agent=None))
    assert plan.tasks[0].agent == "research"
    assert plan.tasks[0].capability == "general"
