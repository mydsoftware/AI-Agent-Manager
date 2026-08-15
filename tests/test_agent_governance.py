from agents.registry import create_default_registry
from agents.registry_manager import AgentRegistryManager
from manager.agent_governance import AgentGovernance
from manager.decision import DecisionEngine
from manager.intention import UserIntent


def test_governance_controls_agent_selection():
    registry = create_default_registry()
    manager = AgentRegistryManager(registry)
    governance = AgentGovernance(manager)

    assert governance.can_use("developer")
    manager.disable("developer")
    assert not governance.can_use("developer")

    decision = DecisionEngine(governance).decide(UserIntent(goal="build", agent="developer"))
    assert decision.agent != "developer"
    assert decision.agent in governance.available_agents()


def test_governance_fails_when_no_agents_are_available():
    registry = create_default_registry()
    manager = AgentRegistryManager(registry)
    for name in registry.names():
        manager.disable(name)

    try:
        DecisionEngine(AgentGovernance(manager)).decide(UserIntent(goal="build", agent="developer"))
    except RuntimeError as exc:
        assert "هیچ ایجنت فعالی" in str(exc)
    else:
        raise AssertionError("DecisionEngine باید وقتی هیچ ایجنت فعالی نیست خطا بدهد")
