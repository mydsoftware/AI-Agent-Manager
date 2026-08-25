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
        python = shutil.which("python") or shutil.which("python3")
        if not python:
            return WordPressBrowserTestResult(False, False, (), ("missing:python",))

        script = '''from playwright.sync_api import sync_playwright
import sys
import os
url = sys.argv[1]

# اول Chromium، بعد Edge، بعد هر مرورگر موجود
edge_path = r"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
edge_path_alt = r"C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe"

with sync_playwright() as p:
    browser = None
    # تلاش برای Chromium
    try:
        browser = p.chromium.launch(headless=True)
    except Exception:
        pass
    # تلاش برای Edge
    if browser is None:
        for ep in [edge_path, edge_path_alt]:
            if os.path.exists(ep):
                try:
                    browser = p.chromium.launch(headless=True, executable_path=ep)
                    break
                except Exception:
                    pass
    if browser is None:
        print("ERROR: No browser available")
        sys.exit(1)
    page = browser.new_page(viewport={"width": 1280, "height": 720})
    page.goto(url, wait_until="networkidle")
    assert page.locator("body").count() > 0
    assert page.locator("nav").count() > 0
    assert page.locator("main").count() > 0
    page.screenshot(path="browser-smoke.png", full_page=True)
    browser.close()
'''
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as handle:
            handle.write(script)
            script_path = handle.name
        try:
            result = subprocess.run([python, script_path, url], capture_output=True, text=True)
            if result.returncode == 0:
                return WordPressBrowserTestResult(True, True, ("page-rendered", "navigation-rendered", "main-rendered"), ())
            detail = result.stderr[-1000:] or result.stdout[-1000:] or "unknown browser failure"
            return WordPressBrowserTestResult(False, True, (), ("browser-test-failed", detail))
        except Exception as exc:
            return WordPressBrowserTestResult(False, False, (), (f"browser-test-error:{exc}",))
        finally:
            Path(script_path).unlink(missing_ok=True)
