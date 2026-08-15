from agents.agent_factory import AgentFactory, AgentSpecification
from agents.capability import AgentCapability
from agents.capability_registry import CapabilityRegistry
from manager.agent_discovery import AgentDiscovery
from manager.task import Task


def test_factory_creates_registers_and_discovery_finds_agent():
    registry = CapabilityRegistry()
    factory = AgentFactory(registry)
    specification = AgentSpecification(
        name="html-web-designer",
        capability=AgentCapability(
            "web-design",
            "HTML website design",
            frozenset({"html", "css", "javascript"}),
        ),
    )

    agent_class = factory.create(specification)
    discovered = AgentDiscovery(registry).discover("html")

    assert discovered is agent_class
    assert agent_class.name == "html-web-designer"
    result = agent_class().run(Task("1", "Build HTML site", "create a website", "html-web-designer"))
    assert "Build HTML site" in result
