from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess
import time
import urllib.request

from agents.wordpress_local_runtime_agent import WordPressLocalRuntimeAgent
from agents.wordpress_browser_test_agent import WordPressBrowserTestAgent, WordPressBrowserTestResult


@dataclass(frozen=True)
class RuntimeBrowserResult:
    runtime_url: str | None
    browser: WordPressBrowserTestResult
    started: bool
    stopped: bool


class WordPressRuntimeBrowserRunner:
    """Runtime محلی را بالا می‌آورد، Browser Test را اجرا و پردازش را متوقف می‌کند."""

    def __init__(self) -> None:
        self.runtime = WordPressLocalRuntimeAgent()
        self.browser = WordPressBrowserTestAgent()

    def run(self, root: str, port: int = 8765) -> RuntimeBrowserResult:
        prepared = self.runtime.prepare(root, port)
        if not prepared.prepared or not prepared.command or not prepared.url:
            return RuntimeBrowserResult(None, WordPressBrowserTestResult(False, False, (), prepared.findings), False, False)

        process = subprocess.Popen(prepared.command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        started = False
        try:
            for _ in range(20):
                try:
                    with urllib.request.urlopen(prepared.url, timeout=0.5):
                        started = True
                        break
                except Exception:
                    time.sleep(0.1)
            if not started:
                return RuntimeBrowserResult(prepared.url, WordPressBrowserTestResult(False, False, (), ("runtime-not-ready",)), True, False)
            browser = self.browser.run(prepared.url)
            return RuntimeBrowserResult(prepared.url, browser, True, True)
        finally:
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=2)
