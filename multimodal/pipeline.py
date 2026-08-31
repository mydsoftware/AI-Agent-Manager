"""Multimodal asset pipeline with pluggable providers. Default is local mock."""

from __future__ import annotations

import hashlib
import json
import logging
import time
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Protocol

logger = logging.getLogger(__name__)


@dataclass
class AssetRequest:
    kind: str
    prompt: str
    project_id: str = "default"
    name: str = ""
    extras: dict | None = None


@dataclass
class AssetResult:
    id: str
    kind: str
    path: str
    prompt: str
    provider: str
    review_status: str
    metadata: dict


class AssetProvider(Protocol):
    name: str
    kinds: set[str]

    def generate(self, request: AssetRequest, out_dir: Path) -> AssetResult: ...


class MockProvider:
    name = "mock"
    kinds = {"image", "audio", "music", "speech", "model3d"}

    def generate(self, request: AssetRequest, out_dir: Path) -> AssetResult:
        digest = hashlib.sha256(f"{request.kind}:{request.prompt}".encode()).hexdigest()[:12]
        ext = {
            "image": "svg",
            "audio": "txt",
            "music": "txt",
            "speech": "txt",
            "model3d": "json",
        }.get(request.kind, "txt")
        name = request.name or f"{request.kind}_{digest}.{ext}"
        dest = out_dir / request.project_id / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        if request.kind == "image":
            dest.write_text(
                f'<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256">'
                f'<rect width="256" height="256" fill="#1e293b"/>'
                f'<text x="16" y="128" fill="#38bdf8" font-size="14">{request.prompt[:40]}</text></svg>',
                encoding="utf-8",
            )
        else:
            dest.write_text(f"MOCK {request.kind}\n{request.prompt}\n", encoding="utf-8")
        return AssetResult(
            id=str(uuid.uuid4()),
            kind=request.kind,
            path=str(dest),
            prompt=request.prompt,
            provider=self.name,
            review_status="pending_review",
            metadata={"digest": digest, "created_at": time.time()},
        )


class AssetManager:
    def __init__(self, output_dir: str = "asset_generation/output", default: str = "mock") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.providers: dict[str, AssetProvider] = {"mock": MockProvider()}
        self.default = default if default in self.providers else "mock"
        self.catalog_path = self.output_dir / "catalog.json"
        self.catalog: list[dict] = []
        if self.catalog_path.exists():
            self.catalog = json.loads(self.catalog_path.read_text(encoding="utf-8"))

    def register(self, provider: AssetProvider) -> None:
        self.providers[provider.name] = provider

    def generate(self, request: AssetRequest, provider_name: str | None = None) -> AssetResult:
        name = provider_name or self.default
        provider = self.providers.get(name) or self.providers["mock"]
        if request.kind not in provider.kinds:
            provider = self.providers["mock"]
        result = provider.generate(request, self.output_dir)
        self.catalog.append(asdict(result))
        self.catalog_path.write_text(json.dumps(self.catalog, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.info("asset %s kind=%s path=%s", result.id, result.kind, result.path)
        return result
