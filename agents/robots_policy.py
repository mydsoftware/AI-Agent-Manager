from __future__ import annotations

from dataclasses import dataclass, field
from urllib.parse import urlparse


@dataclass
class RobotsGroup:
    user_agents: list[str] = field(default_factory=list)
    allow: list[str] = field(default_factory=list)
    disallow: list[str] = field(default_factory=list)


class RobotsPolicy:
    """تحلیل قوانین robots.txt برای User-Agent مربوط به Agent."""

    def __init__(self, user_agent: str = "AI-Agent-Manager") -> None:
        self.user_agent = user_agent
        self.groups: list[RobotsGroup] = []

    def parse(self, text: str) -> None:
        self.groups = []
        current: RobotsGroup | None = None
        for raw in text.splitlines():
            line = raw.split("#", 1)[0].strip()
            if not line or ":" not in line:
                continue
            key, value = line.split(":", 1)
            key, value = key.strip().lower(), value.strip()
            if key == "user-agent":
                if current is None or current.allow or current.disallow or current.user_agents:
                    current = RobotsGroup()
                    self.groups.append(current)
                current.user_agents.append(value.lower())
            elif current is not None and key == "allow":
                current.allow.append(value)
            elif current is not None and key == "disallow":
                current.disallow.append(value)

    def is_allowed(self, url: str) -> bool:
        path = urlparse(url).path or "/"
        groups = self._matching_groups()
        if not groups:
            return True
        rules = [rule for group in groups for rule in self._rules(group, path)]
        if not rules:
            return True
        # در تعارض Allow و Disallow، قانون با مسیر طولانی‌تر اولویت دارد.
        rules.sort(key=lambda item: (len(item[1]), item[0] == "allow"), reverse=True)
        return rules[0][0] == "allow"

    def _matching_groups(self) -> list[RobotsGroup]:
        agent = self.user_agent.lower()
        exact = [g for g in self.groups if agent in g.user_agents]
        wildcard = [g for g in self.groups if "*" in g.user_agents]
        return exact or wildcard

    @staticmethod
    def _rules(group: RobotsGroup, path: str) -> list[tuple[str, str]]:
        result: list[tuple[str, str]] = []
        for rule in group.allow:
            if rule and path.startswith(rule):
                result.append(("allow", rule))
        for rule in group.disallow:
            if rule and path.startswith(rule):
                result.append(("disallow", rule))
        return result
