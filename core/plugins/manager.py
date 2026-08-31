"""Dynamic plugin loader for tools, agents, providers, and adapters."""

from __future__ import annotations

import importlib.util
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger(__name__)

ALLOWED_TYPES = {"tool", "agent", "provider", "adapter"}
ALLOWED_PERMS = {
    "memory.read", "memory.write", "tools.register", "agents.register",
    "network", "fs.read", "fs.write",
}


@dataclass
class PluginManifest:
    name: str
    version: str
    description: str
    type: str
    entrypoint: str
    permissions: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    config_schema: dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    path: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any], path: str = "") -> "PluginManifest":
        return cls(
            name=str(data["name"]),
            version=str(data.get("version", "0.0.0")),
            description=str(data.get("description", "")),
            type=str(data["type"]),
            entrypoint=str(data["entrypoint"]),
            permissions=list(data.get("permissions") or []),
            dependencies=list(data.get("dependencies") or []),
            config_schema=dict(data.get("config_schema") or {}),
            enabled=bool(data.get("enabled", True)),
            path=path,
        )


class PluginError(Exception):
    pass


class PluginManager:
    def __init__(self, plugins_dir: str = "plugins") -> None:
        self.plugins_dir = Path(plugins_dir)
        self.manifests: dict[str, PluginManifest] = {}
        self.loaded: dict[str, Any] = {}
        self.errors: dict[str, str] = {}

    def validate(self, manifest: PluginManifest) -> list[str]:
        errors: list[str] = []
        if not manifest.name:
            errors.append("missing name")
        if manifest.type not in ALLOWED_TYPES:
            errors.append(f"invalid type {manifest.type}")
        if not manifest.entrypoint:
            errors.append("missing entrypoint")
        for perm in manifest.permissions:
            if perm not in ALLOWED_PERMS:
                errors.append(f"unknown permission {perm}")
        return errors

    def discover(self) -> list[PluginManifest]:
        found: list[PluginManifest] = []
        if not self.plugins_dir.exists():
            return found
        for manifest_path in self.plugins_dir.rglob("plugin.json"):
            try:
                data = json.loads(manifest_path.read_text(encoding="utf-8"))
                m = PluginManifest.from_dict(data, str(manifest_path.parent))
                errs = self.validate(m)
                if errs:
                    self.errors[m.name or str(manifest_path)] = "; ".join(errs)
                    logger.warning("rejected plugin %s: %s", manifest_path, errs)
                    continue
                self.manifests[m.name] = m
                found.append(m)
            except Exception as exc:
                self.errors[str(manifest_path)] = str(exc)
                logger.warning("invalid plugin manifest %s: %s", manifest_path, exp if False else exc)
        return found

    def load(self, name: str) -> Any:
        m = self.manifests[name]
        if not m.enabled:
            raise PluginError(f"plugin disabled: {name}")
        module_file = Path(m.path) / m.entrypoint
        spec = importlib.util.spec_from_file_location(f"plugin_{name}", module_file)
        if spec is None or spec.loader is None:
            raise PluginError(f"cannot load {module_file}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.loaded[name] = module
        return module

    def load_all(self, register: Callable[[PluginManifest, Any], None] | None = None) -> None:
        self.discover()
        for name, manifest in list(self.manifests.items()):
            if not manifest.enabled:
                continue
            try:
                module = self.load(name)
                if register:
                    register(manifest, module)
            except Exception as exc:
                self.errors[name] = str(exc)
                logger.exception("plugin %s failed to load", name)

    def status(self) -> dict[str, Any]:
        return {"discovered": list(self.manifests), "loaded": list(self.loaded), "errors": dict(self.errors)}
