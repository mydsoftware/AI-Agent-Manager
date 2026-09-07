"""اجرای QA مرورگر برای Preview/Production بدون افشای جزئیات داخلی Agent."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from services.url_security import validate_public_http_url


@dataclass(frozen=True)
class BrowserCheck:
    """نتیجه یک بررسی Smoke Test مرورگر را نگه می‌دارد."""

    name: str
    passed: bool
    details: str = ""


class BrowserQA:
    """لایه مستقل QA با کنترل egress برای Navigation، Redirect و Subresource."""

    def __init__(self, browser_factory: Callable[[], Any] | None = None) -> None:
        """Factory اختیاری مرورگر را برای اجرای QA نگه می‌دارد."""
        self.browser_factory = browser_factory

    def validate_url(self, url: str) -> str:
        """URL مقصد QA را فقط در صورت HTTP(S) و عمومی بودن Host تأیید می‌کند."""
        return validate_public_http_url(url)

    @staticmethod
    def _request_url(request: Any) -> str:
        """URL را از Request Playwright یا Fake Request استخراج می‌کند."""
        return str(getattr(request, "url", ""))

    def _guard_route(self, route: Any) -> None:
        """هر Route را پیش از ارسال به شبکه اعتبارسنجی می‌کند."""
        request = getattr(route, "request", None)
        request_url = self._request_url(request)
        try:
            validate_public_http_url(request_url)
        except ValueError:
            abort = getattr(route, "abort", None)
            if callable(abort):
                abort()
            return
        continue_request = getattr(route, "continue_", None)
        if callable(continue_request):
            continue_request()

    def _guard_requests(self, page: Any) -> None:
        """در صورت نبود Route API، Request event را به‌عنوان دفاع عمقی کنترل می‌کند."""
        if hasattr(page, "route"):
            page.route("**/*", self._guard_route)
            return
        if not hasattr(page, "on"):
            return

        def guard(request: Any) -> None:
            """Request مرورگر را اعتبارسنجی و در صورت ناامن بودن متوقف می‌کند."""
            request_url = self._request_url(request)
            try:
                validate_public_http_url(request_url)
            except ValueError:
                abort = getattr(request, "abort", None)
                if callable(abort):
                    abort()

        page.on("request", guard)

    @staticmethod
    def _new_page_with_service_workers_blocked(browser: Any) -> tuple[Any, Any]:
        """Context جدید Playwright را با Service Worker مسدود و Page آن را ایجاد می‌کند."""
        new_context = getattr(browser, "new_context", None)
        if not callable(new_context):
            return browser, browser.new_page()
        context = new_context(service_workers="block")
        return context, context.new_page()

    def run_smoke(self, url: str) -> dict[str, Any]:
        """یک Smoke Test محدود اجرا می‌کند و نتیجه بررسی بارگذاری و عنوان صفحه را برمی‌گرداند."""
        target = self.validate_url(url)
        if self.browser_factory is None:
            return {"url": target, "status": "not_configured", "checks": []}

        browser = self.browser_factory()
        context = None
        page = None
        checks: list[BrowserCheck] = []
        try:
            context, page = self._new_page_with_service_workers_blocked(browser)
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
                if context is not None and context is not browser:
                    context.close()
                else:
                    browser.close()
            except Exception:
                pass
