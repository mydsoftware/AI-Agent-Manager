from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess
import tempfile


@dataclass(frozen=True)
class WordPressBrowserTestResult:
    passed: bool
    executed: bool
    checks: tuple[str, ...]
    findings: tuple[str, ...]


class WordPressBrowserTestAgent:
    """اجرای تست Browser واقعی با Playwright در صورت نصب بودن Chromium/Playwright."""

    def run(self, url: str) -> WordPressBrowserTestResult:
        if not shutil.which("python"):
            return WordPressBrowserTestResult(False, False, (), ("missing:python",))
        script = '''from playwright.sync_api import sync_playwright
import sys
url = sys.argv[1]
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1280, "height": 720})
    page.goto(url, wait_until="networkidle")
    assert page.title() or page.locator("body").count()
    assert page.locator("nav").count() > 0
    assert page.locator("main").count() > 0
    page.screenshot(path="browser-smoke.png", full_page=True)
    browser.close()
'''
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as handle:
            handle.write(script)
            script_path = handle.name
        try:
            result = subprocess.run(["python", "-m", "playwright", "run", script_path, url], capture_output=True, text=True)
            if result.returncode == 0:
                return WordPressBrowserTestResult(True, True, ("page-rendered", "navigation-rendered", "main-rendered"), ())
            return WordPressBrowserTestResult(False, True, (), ("browser-test-failed", result.stderr[-1000:] or result.stdout[-1000:],))
        except Exception as exc:
            return WordPressBrowserTestResult(False, False, (), (f"browser-test-error:{exc}",))
        finally:
            Path(script_path).unlink(missing_ok=True)
