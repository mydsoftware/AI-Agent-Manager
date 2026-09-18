from manager.intent_router import IntentRouter
from manager.multi_plan import MultiAgentPlanner
from manager.intention import UserIntent


def test_code_routes_to_developer_coder_capability() -> None:
    decision = IntentRouter().classify("یک کد پایتون بنویس")
    assert decision.intent == "coding"
    assert decision.capability == "coder"
    assert decision.role == "developer"


def test_test_routes_to_qa_coding_capability() -> None:
    decision = IntentRouter().classify("تست pytest برای پروژه بنویس")
    assert decision.intent == "testing"
    assert decision.capability == "coding"
    assert decision.role == "qa"


def test_research_routes_to_research_general_capability() -> None:
    decision = IntentRouter().classify("تحقیق درباره معماری سیستم")
    assert decision.intent == "research"
    assert decision.capability == "general"
    assert decision.role == "research"


def test_vision_routes_to_developer_vision_capability() -> None:
    decision = IntentRouter().classify("این اسکرین‌شات را بررسی کن")
    assert decision.intent == "vision"
    assert decision.capability == "vision"
    assert decision.role == "developer"


def test_default_routes_to_developer_general_capability() -> None:
    decision = IntentRouter().classify("یک کار معمولی انجام بده")
    assert decision.intent == "general"
    assert decision.capability == "general"
    assert decision.role == "developer"


def test_planner_preserves_vision_capability() -> None:
    plan = MultiAgentPlanner().plan(UserIntent(goal="این تصویر را بررسی کن"))
    assert len(plan.tasks) == 1
    assert plan.tasks[0].agent == "developer"
    assert plan.tasks[0].capability == "vision"
