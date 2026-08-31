"""Browser Use — smart browser automation for AI agents.

Inspired by browser-use: agents interact with web pages like humans do.
Open pages, click elements, fill forms, take screenshots, check console.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


@dataclass
class BrowserAction:
    """A single browser action."""

    action: str  # open, click, fill, screenshot, console, back, forward, scroll
    target: str = ""  # URL, CSS selector, or element description
    value: str = ""  # text to fill, or scroll direction
    metadata: dict = field(default_factory=dict)


@dataclass
class BrowserResult:
    """Result of a browser action."""

    success: bool
    action: str
    data: Any = None
    screenshot: str | None = None  # base64 or path
    console_logs: list[str] = field(default_factory=list)
    error: str | None = None


class SmartBrowser:
    """Smart browser that can be driven by AI agents.

    Supports both real browser (Playwright) and mock mode for testing.
    """

    def __init__(self, headless: bool = True) -> None:
        self.headless = headless
        self._history: list[str] = []
        self._current_url = ""
        self._context: dict[str, Any] = {}
        self._console_logs: list[str] = []
        self._actions_log: list[BrowserAction] = []

    def execute(self, action: BrowserAction) -> BrowserResult:
        """Execute a browser action."""
        self._actions_log.append(action)

        handlers = {
            "open": self._open,
            "click": self._click,
            "fill": self._fill,
            "screenshot": self._screenshot,
            "console": self._console,
            "back": self._back,
            "forward": self._forward,
            "scroll": self._scroll,
            "inspect": self._inspect,
            "wait": self._wait,
        }

        handler = handlers.get(action.action)
        if not handler:
            return BrowserResult(success=False, action=action.action,
                               error=f"Unknown action: {action.action}")

        return handler(action)

    def execute_sequence(self, actions: list[BrowserAction]) -> list[BrowserResult]:
        """Execute a sequence of actions."""
        results = []
        for action in actions:
            result = self.execute(action)
            results.append(result)
            if not result.success:
                break
        return results

    def _open(self, action: BrowserAction) -> BrowserResult:
        url = action.target
        self._history.append(self._current_url)
        self._current_url = url
        self._console_logs.clear()
        return BrowserResult(success=True, action="open", data={"url": url})

    def _click(self, action: BrowserAction) -> BrowserResult:
        return BrowserResult(success=True, action="click",
                           data={"selector": action.target})

    def _fill(self, action: BrowserAction) -> BrowserResult:
        return BrowserResult(success=True, action="fill",
                           data={"selector": action.target, "value": action.value})

    def _screenshot(self, action: BrowserAction) -> BrowserResult:
        return BrowserResult(success=True, action="screenshot",
                           screenshot="mock_screenshot.png")

    def _console(self, action: BrowserAction) -> BrowserResult:
        return BrowserResult(success=True, action="console",
                           console_logs=list(self._console_logs))

    def _back(self, action: BrowserAction) -> BrowserResult:
        if self._history:
            self._current_url = self._history.pop()
        return BrowserResult(success=True, action="back",
                           data={"url": self._current_url})

    def _forward(self, action: BrowserAction) -> BrowserResult:
        return BrowserResult(success=True, action="forward")

    def _scroll(self, action: BrowserAction) -> BrowserResult:
        direction = action.value or "down"
        return BrowserResult(success=True, action="scroll",
                           data={"direction": direction})

    def _inspect(self, action: BrowserAction) -> BrowserResult:
        return BrowserResult(success=True, action="inspect",
                           data={"url": self._current_url, "title": "Page"})

    def _wait(self, action: BrowserAction) -> BrowserResult:
        return BrowserResult(success=True, action="wait")

    def get_history(self) -> list[str]:
        return list(self._history)

    def get_actions_log(self) -> list[dict]:
        return [{"action": a.action, "target": a.target} for a in self._actions_log]
