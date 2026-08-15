from agents.registry import create_default_registry
from agents.registry_manager import AgentRegistryManager
from manager.agent_governance import AgentGovernance
from manager.decision import DecisionEngine
from manager.intention import IntentParser


def test_full_intent_decision_governance_chain():
    registry = create_default_registry()
    registry_manager = AgentRegistryManager(registry)
    governance = AgentGovernance(registry_manager)

    intent = IntentParser().parse("برای گیتهاب تست انجام بده")
    decision = DecisionEngine(governance).decide(intent)

    assert decision.agent == "github"
    assert governance.can_use(decision.agent)
    assert decision.confidence == 0.9
