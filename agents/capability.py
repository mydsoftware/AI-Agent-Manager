from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AgentCapability:
    """قابلیت قابل ارائه توسط یک ایجنت."""

    name: str
    description: str = ""
    tags: frozenset[str] = field(default_factory=frozenset)

    def matches(self, requested: str) -> bool:
        query = requested.strip().lower()
        return query == self.name.lower() or query in {tag.lower() for tag in self.tags}
