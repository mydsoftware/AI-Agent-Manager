from manager.intention import UserIntent
from manager.multi_plan import MultiAgentPlanner


def test_vision_plan_uses_developer_with_vision_capability() -> None:
    plan = MultiAgentPlanner().plan(UserIntent(goal="این اسکرین‌شات را بررسی کن", agent=None))

    assert len(plan.tasks) == 1
    assert plan.tasks[0].agent == "developer"
    assert plan.tasks[0].capability == "vision"


def test_code_plan_uses_coder_capability() -> None:
    plan = MultiAgentPlanner().plan(UserIntent(goal="این کد را اصلاح کن", agent=None))

    assert plan.tasks[0].agent == "developer"
    assert plan.tasks[0].capability == "coder"


def test_research_plan_uses_research_agent() -> None:
    plan = MultiAgentPlanner().plan(UserIntent(goal="تحقیق درباره معماری سیستم", agent=None))

    assert plan.tasks[0].agent == "research"
    assert plan.tasks[0].capability == "general"
