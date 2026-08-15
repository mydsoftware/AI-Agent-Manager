from agents.base_agent import BaseAgent
from agents.capability import AgentCapability
from agents.capability_registry import CapabilityRegistry
from manager.agent_discovery import AgentDiscovery


class HtmlAgent(BaseAgent):
    name = "html-web-designer"

    def run(self, task):
        return "ok"


def test_discovery_finds_agent_by_capability_tag():
    registry = CapabilityRegistry()
    registry.register(
        HtmlAgent,
        [AgentCapability("web-design", "HTML website design", frozenset({"html", "css", "javascript"}))],
    )

    discovery = AgentDiscovery(registry)

    assert discovery.discover("html") is HtmlAgent
    assert discovery.discover("css") is HtmlAgent
    assert discovery.discover("python") is None
