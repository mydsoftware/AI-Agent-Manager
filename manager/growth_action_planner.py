from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from manager.growth_actions import GrowthAction


@dataclass(frozen=True)
class PlannedAction:
    action: GrowthAction
    key: str


class GrowthActionPlanner:
    """خروجی Agent را به actionهای معتبر، یکتا و قابل اجرای Growth Engine تبدیل می‌کند."""

    def plan(self, raw_result: str, phase: str) -> list[PlannedAction]:
        if not isinstance(raw_result, str):
            return []

        try:
            data = json.loads(raw_result)
        except (TypeError, json.JSONDecodeError):
            return []

        raw_actions = data.get("actions", [])
        if not isinstance(raw_actions, list):
            return []

        planned: list[PlannedAction] = []
        seen: set[str] = set()

        for item in raw_actions:
            if not isinstance(item, dict):
                continue

            name = str(item.get("name", "")).strip()
            if not name:
                continue

            payload = item.get("payload", {})
            if not isinstance(payload, dict):
                payload = {"value": payload}

            action_phase = str(item.get("phase", phase)).strip() or phase
            action = GrowthAction(name=name, phase=action_phase, payload=payload)
            key = self.idempotency_key(action)

            if key in seen:
                continue

            seen.add(key)
            planned.append(PlannedAction(action=action, key=key))

        return planned

    @staticmethod
    def idempotency_key(action: GrowthAction) -> str:
        canonical = json.dumps(
            {
                "name": action.name,
                "phase": action.phase,
                "payload": action.payload,
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
