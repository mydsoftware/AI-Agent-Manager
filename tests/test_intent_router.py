from manager.intent_router import IntentRouter


def test_code_routes_to_registered_developer_agent() -> None:
    decision = IntentRouter().classify("این کد را اصلاح کن")
    assert decision.intent == "coding"
    assert decision.capability == "coder"
    assert decision.role == "developer"


def test_test_routes_to_qa_agent() -> None:
    decision = IntentRouter().classify("تست e2e پروژه را اجرا کن")
    assert decision.intent == "testing"
    assert decision.capability == "coding"
    assert decision.role == "qa"


def test_research_routes_to_research_agent() -> None:
    decision = IntentRouter().classify("تحقیق درباره معماری سیستم")
    assert decision.intent == "research"
    assert decision.role == "research"


def test_vision_is_explicitly_marked_as_vision_capability() -> None:
    decision = IntentRouter().classify("این اسکرین‌شات را بررسی کن")
    assert decision.intent == "vision"
    assert decision.capability == "vision"
    assert decision.role == "developer"
