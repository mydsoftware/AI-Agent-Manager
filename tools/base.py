"""کلاس پایه و قرارداد ابزارها."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ToolPermission(str, Enum):
    """مجوزهای اجرایی ابزارها."""

    READ_FILE = "read_file"
    WRITE_FILE = "write_file"
    DELETE_FILE = "delete_file"
    EXECUTE_COMMAND = "execute_command"
    GIT = "git"
    GITHUB = "github"
    DEPLOY = "deploy"
    NETWORK = "network"
    BROWSER = "browser"


@dataclass(frozen=True)
class ToolResult:
    """نتیجه اجرای یک ابزار."""

    success: bool
    output: str = ""
    error: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class Tool(ABC):
    """قرارداد مشترک تمام ابزارها."""

    name: str = "base"
    description: str = ""
    permissions: list[ToolPermission] = field(default_factory=list)
    timeout: float = 30.0

    @abstractmethod
    def execute(self, **kwargs: Any) -> ToolResult:
        """ابزار را اجرا می‌کند."""
        raise NotImplementedError

    def validate(self, **kwargs: Any) -> bool:
        """ورودی‌ها را اعتبارسنجی می‌کند."""
        return True

    def to_schema(self) -> dict[str, Any]:
        """Schema ابزار را برای LLM برمی‌گرداند."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {},
                },
            },
        }
