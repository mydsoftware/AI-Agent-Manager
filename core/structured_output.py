"""Structured Output — PydanticAI-style validation for Agent responses.

Ensures every agent produces valid, schema-conformant output.
Invalid output triggers automatic retry/repair.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class OutputSchema:
    """Defines expected output structure for an agent."""

    name: str
    fields: dict[str, dict] = field(default_factory=dict)
    required: list[str] = field(default_factory=list)
    validator: Callable | None = None

    def validate(self, data: dict) -> tuple[bool, list[str]]:
        """Validate data against schema. Returns (valid, errors)."""
        errors = []

        for field_name in self.required:
            if field_name not in data:
                errors.append(f"Missing required field: {field_name}")

        for field_name, rules in self.fields.items():
            if field_name in data:
                value = data[field_name]
                expected_type = rules.get("type")
                if expected_type and not isinstance(value, _PYTHON_TYPES.get(expected_type, object)):
                    errors.append(f"Field '{field_name}' must be {expected_type}, got {type(value).__name__}")

                if "enum" in rules and value not in rules["enum"]:
                    errors.append(f"Field '{field_name}' must be one of {rules['enum']}")

                if "min_length" in rules and isinstance(value, str) and len(value) < rules["min_length"]:
                    errors.append(f"Field '{field_name}' too short (min {rules['min_length']})")

        if self.validator:
            try:
                ok, msg = self.validator(data)
                if not ok:
                    errors.append(msg)
            except Exception as e:
                errors.append(f"Custom validator error: {e}")

        return len(errors) == 0, errors


# Predefined schemas for common agent outputs
TASK_SCHEMA = OutputSchema(
    name="task",
    fields={
        "id": {"type": "str"},
        "type": {"type": "str", "enum": ["create", "edit", "delete", "test", "review", "deploy"]},
        "description": {"type": "str", "min_length": 5},
        "status": {"type": "str", "enum": ["pending", "running", "completed", "failed"]},
        "agent": {"type": "str"},
        "priority": {"type": "int"},
    },
    required=["id", "type", "description"],
)

PLAN_SCHEMA = OutputSchema(
    name="plan",
    fields={
        "tasks": {"type": "list"},
        "strategy": {"type": "str"},
        "estimated_time": {"type": "str"},
    },
    required=["tasks", "strategy"],
)

CODE_SCHEMA = OutputSchema(
    name="code",
    fields={
        "files": {"type": "list"},
        "language": {"type": "str"},
        "description": {"type": "str"},
    },
    required=["files", "language"],
)

GAME_DESIGN_SCHEMA = OutputSchema(
    name="game_design",
    fields={
        "genre": {"type": "str"},
        "platform": {"type": "str"},
        "engine": {"type": "str"},
        "mechanics": {"type": "list"},
        "art_style": {"type": "str"},
    },
    required=["genre", "platform", "engine"],
)


class StructuredOutput:
    """Wraps agent output with validation and repair."""

    def __init__(self, schema: OutputSchema, max_retries: int = 3) -> None:
        self.schema = schema
        self.max_retries = max_retries

    def validate_and_repair(self, raw_output: str | dict) -> tuple[dict | None, list[str]]:
        """Validate output, attempt repair if invalid."""
        data = self._parse(raw_output)

        for attempt in range(self.max_retries):
            valid, errors = self.schema.validate(data)
            if valid:
                return data, []

            # Attempt repair
            data = self._repair(data, errors)

        return data, errors

    def _parse(self, raw: str | dict) -> dict:
        """Parse raw output to dict."""
        if isinstance(raw, dict):
            return raw
        if isinstance(raw, str):
            # Try JSON
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                pass
            # Try extracting JSON from markdown
            match = re.search(r"```(?:json)?\s*\n(.*?)\n```", raw, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    pass
            # Fallback: wrap as text
            return {"text": raw, "_unstructured": True}
        return {}

    def _repair(self, data: dict, errors: list[str]) -> dict:
        """Attempt to fix common issues."""
        repaired = dict(data)

        for error in errors:
            if "Missing required field" in error:
                field_name = error.split(": ")[-1]
                defaults = {
                    "id": "auto",
                    "type": "create",
                    "status": "pending",
                    "priority": 5,
                    "agent": "developer",
                    "description": "Auto-generated task",
                    "tasks": [],
                    "strategy": "sequential",
                    "files": [],
                    "language": "python",
                    "genre": "platformer",
                    "platform": "web",
                    "engine": "godot",
                    "mechanics": [],
                    "art_style": "pixel_art",
                    "estimated_time": "unknown",
                }
                if field_name in defaults:
                    repaired[field_name] = defaults[field_name]

            elif "must be one of" in error:
                # Extract field name and set first valid enum value
                match = re.search(r"Field '(\w+)'", error)
                if match:
                    field_name = match.group(1)
                    rules = self.schema.fields.get(field_name, {})
                    if "enum" in rules and rules["enum"]:
                        repaired[field_name] = rules["enum"][0]

        return repaired


_PYTHON_TYPES = {
    "str": str,
    "int": int,
    "float": (int, float),
    "bool": bool,
    "list": list,
    "dict": dict,
}
