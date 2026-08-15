from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WordPressAccessibilityTestResult:
    passed: bool
    checks: tuple[str, ...]
    findings: tuple[str, ...]


class WordPressAccessibilityTestAgent:
    """Checks basic accessibility requirements in a rendered page."""

    def run(self, url: str) -> WordPressAccessibilityTestResult:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return WordPressAccessibilityTestResult(False, (), ("missing:playwright",))

        checks: list[str] = []
        findings: list[str] = []
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=15000)
                if page.title().strip():
                    checks.append("title-present")
                else:
                    findings.append("missing:title")
                images = page.locator("img")
                missing_alt = sum(1 for i in range(images.count()) if images.nth(i).get_attribute("alt") is None)
                if missing_alt:
                    findings.append(f"missing:alt:{missing_alt}")
                else:
                    checks.append("image-alt")
                if page.locator("h1").count() >= 1:
                    checks.append("heading-h1")
                else:
                    findings.append("missing:h1")
                if page.locator("input,textarea,select").count() == 0 or page.locator("label").count() > 0:
                    checks.append("form-labels")
                else:
                    findings.append("missing:form-labels")
            except Exception as exc:
                findings.append(f"browser-error:{type(exc).__name__}")
            finally:
                browser.close()
        return WordPressAccessibilityTestResult(not findings, tuple(checks), tuple(findings))
