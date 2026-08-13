from dataclasses import dataclass, field
from typing import List


@dataclass
class Task:
    id: str
    title: str
    description: str
    agent: str
    depends_on: List[str] = field(default_factory=list)
    status: str = "pending"
    result: str | None = None
