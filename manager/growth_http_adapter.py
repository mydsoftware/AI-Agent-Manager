from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from manager.growth_actions import GrowthAction


@dataclass(frozen=True)
class HTTPGrowthAdapter:
    """Adapter عمومی HTTPS برای Providerهایی که webhook/API سازگار دارند."""

    base_url: str
    api_key: str | None = None
    timeout: float = 15.0

    def execute(self, action: GrowthAction) -> dict[str, Any]:
        url = self.base_url.rstrip("/") + "/" + action.name.lstrip("/")
        payload = json.dumps(action.payload, ensure_ascii=False).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        request = urllib.request.Request(url, data=payload, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8", errors="replace")
                try:
                    data = json.loads(raw) if raw else {}
                except json.JSONDecodeError:
                    data = {"response": raw}
                return {
                    "status": "executed",
                    "action": action.name,
                    "phase": action.phase,
                    "external_execution": True,
                    "data": {"http_status": response.status, "response": data},
                }
        except (urllib.error.URLError, TimeoutError) as error:
            return {
                "status": "failed",
                "action": action.name,
                "phase": action.phase,
                "external_execution": True,
                "data": {"error": str(error)},
            }
