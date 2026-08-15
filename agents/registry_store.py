from __future__ import annotations

import json
from pathlib import Path

from agents.registry_manager import AgentRecord, AgentRegistryManager


class AgentRegistryStore:
    """وضعیت Agent Registry را روی دیسک ذخیره و بازیابی می‌کند."""

    def __init__(self, path: str = "data/agents.json") -> None:
        self.path = Path(path)

    def save(self, manager: AgentRegistryManager) -> None:
        """وضعیت Agentها را ذخیره می‌کند."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        records = {
            name: {
                "enabled": record.enabled,
                "description": record.description,
            }
            for name, record in manager._records.items()
        }
        self.path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")

    def load(self, manager: AgentRegistryManager) -> None:
        """وضعیت ذخیره‌شده را روی Agentهای ثبت‌شده اعمال می‌کند."""
        if not self.path.exists():
            return
        records = json.loads(self.path.read_text(encoding="utf-8"))
        for name, data in records.items():
            if name not in manager._records:
                continue
            manager._records[name] = AgentRecord(
                name=name,
                enabled=bool(data.get("enabled", True)),
                description=str(data.get("description", "")),
            )
