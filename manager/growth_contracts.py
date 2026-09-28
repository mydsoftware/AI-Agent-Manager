from __future__ import annotations

from dataclasses import asdict, dataclass
import json


@dataclass(frozen=True)
class GrowthArtifact:
    kind: str
    phase: str
    status: str
    payload: dict

    def dumps(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)


def parse_artifact(raw: str) -> GrowthArtifact:
    data = json.loads(raw)
    return GrowthArtifact(
        kind=str(data.get("type", "business_growth_result")),
        phase=str(data.get("phase", "unknown")),
        status=str(data.get("status", "ready")),
        payload=data,
    )
