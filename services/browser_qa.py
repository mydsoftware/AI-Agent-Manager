"""اجرای QA مرورگر برای Preview/Production بدون افشای جزئیات داخلی Agent."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from services.url_security import validate_public_http_url


@dataclass(frozen=True)
class BrowserCheck:
    name: str
    passed: bool
    details: str = ""


class BrowserQA:
    """لایه مستقل QA که می‌تواند به Playwright یا Browser Agent متصل شود."""

    def __init__(self, browser_factory: Callable[[], Any] | None = None) -> None:
        """Factory اختیاری مرورگر را برای اجرای QA نگه می‌دارد."""
        self.browser_factory = browser_factory

    def validate_url(self, url: str) -> str:
        """URL مقصد QA را فقط در صورت HTTP(S) و عمومی بودن Host تأیید می‌کند."""
        return validate_public_http_url(url)

    def _guard_requests(self, page: Any) -> None:
        """هر Request مرورگر را پیش از ارسال دوباره برای جلوگیری از Redirect به شبکه داخلی بررسی می‌کند."""
        if not hasattr(page, "on"):
            return

        def guard(request: Any) -> None:
            """یک Request مرورگر را اعتبارسنجی و در صورت ناامن بودن متوقف می‌کند."""
            request_url = str(getattr(request, "url", ""))
            try:
                validate_public_http_url(request_url)
            except ValueError:
                abort = getattr(request, "abort", None)
                if callable(abort):
                    abort()

        page.on("request", guard)

    def run_smoke(self, url: str) -> dict[str, Any]:
        """یک Smoke Test محدود اجرا می‌کند و نتیجه بررسی بارگذاری و عنوان صفحه را برمی‌گرداند."""
        target = self.validate_url(url)
        if self.browser_factory is None:
            return {"url": target, "status": "not_configured", "checks": []}

        browser = self.browser_factory()
        page = browser.new_page()
        checks: list[BrowserCheck] = []
        try:
            self._guard_requests(page)
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
