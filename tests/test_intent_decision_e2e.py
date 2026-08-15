from manager.intention import IntentParser
from manager.decision import DecisionEngine


def test_intent_and_decision_select_specialist_agent():
    intent = IntentParser().parse("برای پروژه گیتهاب کدنویسی و تست انجام بده")
    decision = DecisionEngine().decide(intent)

    assert intent.agent in {"github", "developer", "qa"}
    assert decision.agent == intent.agent
    assert 0.0 <= decision.confidence <= 1.0


def test_ambiguous_intent_defaults_to_developer():
    intent = IntentParser().parse("یک پروژه جدید بساز")
    decision = DecisionEngine().decide(intent)

    assert intent.agent is None
    assert decision.agent == "developer"
    assert decision.confidence == 0.5
