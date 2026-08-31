#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Builder - ساخت و مدیریت خودکار ایجنت‌ها
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime


DEFAULT_CONFIG = {
    "supported_agent_types": [
        "developer", "research", "qa", "github",
        "monitoring", "analysis", "automation",
    ],
    "tools_priority": ["opencode", "freebuff"],
    "default_language": "python",
}


class AgentBuilder:
    """سازنده ایجنت‌ها با پشتیبانی از OpenCode و Freebuff."""

    def __init__(self, workspace_dir: str = ".", config_path: str = "config.json") -> None:
        self.workspace_dir = Path(workspace_dir)
        self.agents_dir = self.workspace_dir / "agents"
        self.agents_dir.mkdir(parents=True, exist_ok=True)

        self.config = dict(DEFAULT_CONFIG)
        self._load_config(config_path)
        self.selected_tool = self._detect_tool()

    # ── config ──────────────────────────────────────────────
    def _load_config(self, config_path: str) -> None:
        candidates = [
            self.workspace_dir / config_path,
            Path(config_path),
            Path("config.json"),
        ]
        for p in candidates:
            if p.is_file():
                try:
                    data = json.loads(p.read_text(encoding="utf-8"))
                    self.config.update(data)
                except Exception:
                    pass
                return

    def _detect_tool(self) -> str:
        for tool in self.config.get("tools_priority", []):
            if tool == "opencode" and os.getenv("OPENCODE_API_KEY"):
                return "opencode"
            if tool == "freebuff" and os.getenv("FREEBUFF_API_KEY"):
                return "freebuff"
        return self.config.get("tools_priority", ["freebuff"])[0]

    # ── id generation ───────────────────────────────────────
    def _generate_agent_id(self, agent_type: str, description: str) -> str:
        slug = hashlib.md5(description.encode("utf-8")).hexdigest()[:8]
        return f"agent_{agent_type}_{slug}"

    # ── prompt creation ─────────────────────────────────────
    def _create_agent_prompt(self, agent_type: str, description: str, language: str) -> str:
        return (
            f"You are a specialized {agent_type} agent.\n"
            f"Description: {description}\n"
            f"Language: {language}\n"
            f"Follow best practices and produce high-quality output."
        )

    def _build_prompt(self, description: str, details: dict, tool: str) -> str:
        agent_type = details.get("agent_type", "developer")
        language = details.get("language", "python")
        return (
            f"Build the following: {description}\n"
            f"Agent type: {agent_type}\n"
            f"Language: {language}\n"
            f"Tool: {tool}"
        )

    # ── agent CRUD ──────────────────────────────────────────
    def create_agent(
        self,
        agent_type: str,
        description: str,
        language: str = "python",
    ) -> dict:
        if agent_type not in self.config["supported_agent_types"]:
            raise ValueError(f"Unsupported agent type: {agent_type}")

        agent_id = self._generate_agent_id(agent_type, description)
        prompt = self._create_agent_prompt(agent_type, description, language)

        agent = {
            "id": agent_id,
            "type": agent_type,
            "description": description,
            "language": language,
            "tool_used": self.selected_tool,
            "prompt": prompt,
            "created_at": datetime.utcnow().isoformat(),
        }

        agent_file = self.agents_dir / f"{agent_id}.json"
        agent_file.write_text(json.dumps(agent, indent=2, ensure_ascii=False), encoding="utf-8")
        return agent

    def get_agent(self, agent_id: str) -> dict | None:
        agent_file = self.agents_dir / f"{agent_id}.json"
        if agent_file.is_file():
            return json.loads(agent_file.read_text(encoding="utf-8"))
        return None

    def list_agents(self) -> list[dict]:
        agents = []
        for f in sorted(self.agents_dir.glob("agent_*.json")):
            try:
                agents.append(json.loads(f.read_text(encoding="utf-8")))
            except Exception:
                continue
        return agents

    def create_pull_request(self, agent_id: str) -> dict:
        agent = self.get_agent(agent_id)
        if not agent:
            return {"error": "Agent not found"}
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            return {"error": "GITHUB_TOKEN not configured"}
        # Real GitHub integration would go here via adapters/github_adapter.py
        return {"pr_url": None, "message": "GitHub integration requires GITHUB_TOKEN"}
