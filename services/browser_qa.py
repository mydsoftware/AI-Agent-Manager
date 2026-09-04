"""اجرای QA مرورگر برای Preview/Production بدون افشای جزئیات داخلی Agent."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class BrowserCheck:
    name: str
    passed: bool
    details: str = ""


class BrowserQA:
    """لایه مستقل QA که می‌تواند به Playwright یا Browser Agent متصل شود."""

    def __init__(self, browser_factory: Callable[[], Any] | None = None) -> None:
        self.browser_factory = browser_factory

    def validate_url(self, url: str) -> str:
        value = url.strip()
        if not value.startswith(("https://", "http://")):
            raise ValueError("URL باید با http:// یا https:// شروع شود.")
        return value

    def run_smoke(self, url: str) -> dict[str, Any]:
        target = self.validate_url(url)
        if self.browser_factory is None:
            return {"url": target, "status": "not_configured", "checks": []}

        browser = self.browser_factory()
        page = browser.new_page()
        checks: list[BrowserCheck] = []
        try:
            response = page.goto(target, wait_until="domcontentloaded")
            status = getattr(response, "status", None)
            checks.append(BrowserCheck("page_load", bool(status and status < 400), f"HTTP {status}"))
            title = page.title()
            checks.append(BrowserCheck("page_title", bool(title.strip()), title.strip()))
            return {
                "url": target,
                "status": "passed" if all(item.passed for item in checks) else "failed",
                "checks": [item.__dict__ for item in checks],
            }
        finally:
            try:
                browser.close()
            except Exception:
                pass
