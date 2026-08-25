from __future__ import annotations

from dataclasses import dataclass

from agents.browser_launcher import launch_browser
from agents.wordpress_browser_test_agent import WordPressBrowserTestAgent


@dataclass(frozen=True)
class WordPressInteractionTestResult:
    passed: bool
    checks: tuple[str, ...]
    findings: tuple[str, ...]


class WordPressInteractionTestAgent:
    """Browser-based interaction checks for links, forms and buttons."""

    def __init__(self) -> None:
        self.browser = WordPressBrowserTestAgent()

    def run(self, url: str) -> WordPressInteractionTestResult:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return WordPressInteractionTestResult(False, (), ("missing:playwright",))

        checks: list[str] = []
        findings: list[str] = []
        with sync_playwright() as playwright:
            try:
                browser = launch_browser(playwright)
            except RuntimeError:
                return WordPressInteractionTestResult(False, (), ("missing:playwright",))
            page = browser.new_page()
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=15000)
                if page.locator("a[href]").count() > 0:
                    checks.append("links-present")
                else:
                    findings.append("missing:links")
                forms = page.locator("form")
                if forms.count() > 0:
                    checks.append("forms-present")
                    for index in range(forms.count()):
                        if forms.nth(index).locator("input,textarea,select").count() == 0:
                            findings.append(f"empty-form:{index}")
                buttons = page.locator("button, input[type=submit]")
                if buttons.count() > 0:
                    checks.append("buttons-present")
                else:
                    findings.append("missing:buttons")
            except Exception as exc:
                findings.append(f"browser-error:{type(exc).__name__}")
            finally:
                browser.close()
        return WordPressInteractionTestResult(not findings, tuple(checks), tuple(findings))
