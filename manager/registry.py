from dataclasses import dataclass
from typing import Dict, Type


@dataclass(frozen=True)
class AgentSpec:
    name: str
    description: str


class AgentRegistry:
    def __init__(self) -> None:
        self._agents: Dict[str, AgentSpec] = {}

    def register(self, name: str, description: str) -> None:
        self._agents[name] = AgentSpec(name, description)

    def get(self, name: str) -> AgentSpec:
        return self._agents[name]

    def all(self) -> Dict[str, AgentSpec]:
        return dict(self._agents)
