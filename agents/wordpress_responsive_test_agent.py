from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WordPressResponsiveTestResult:
    passed: bool
    checks: tuple[str, ...]
    findings: tuple[str, ...]


class WordPressResponsiveTestAgent:
    """Viewport checks for mobile, tablet and desktop using Playwright."""

    VIEWPORTS = {
        "mobile": (390, 844),
        "tablet": (768, 1024),
        "desktop": (1440, 900),
    }

    def run(self, url: str) -> WordPressResponsiveTestResult:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return WordPressResponsiveTestResult(False, (), ("missing:playwright",))

        checks: list[str] = []
        findings: list[str] = []
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                for name, (width, height) in self.VIEWPORTS.items():
                    page = browser.new_page(viewport={"width": width, "height": height})
                    try:
                        page.goto(url, wait_until="domcontentloaded", timeout=15000)
                        overflow = page.evaluate("document.documentElement.scrollWidth > window.innerWidth")
                        if overflow:
                            findings.append(f"horizontal-overflow:{name}")
                        else:
                            checks.append(f"viewport:{name}")
                    except Exception as exc:
                        findings.append(f"browser-error:{name}:{type(exc).__name__}")
                    finally:
                        page.close()
            finally:
                browser.close()
        return WordPressResponsiveTestResult(not findings, tuple(checks), tuple(findings))
