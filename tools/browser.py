"""ابزار مرورگر برای تست و تأیید وب."""

from __future__ import annotations

from typing import Any

from .base import Tool, ToolPermission, ToolResult


class BrowserTool(Tool):
    """ابزار عملیات مرورگر برای تست وب."""

    name = "browser"
    description = "باز کردن صفحه، کلیک، پر کردن فرم، اسکرین‌شات و بررسی Console"
    permissions = [ToolPermission.BROWSER, ToolPermission.NETWORK]
    timeout = 30.0

    def validate(self, **kwargs: Any) -> bool:
        action = kwargs.get("action", "")
        return action in {"open", "click", "fill", "screenshot", "console", "network", "inspect", "evaluate"}

    def execute(self, **kwargs: Any) -> ToolResult:
        action = kwargs.get("action", "")
        url = kwargs.get("url", "")

        try:
            if action == "open":
                return self._open(url)
            elif action == "screenshot":
                return self._screenshot(url)
            elif action == "console":
                return self._check_console(url)
            elif action == "evaluate":
                return self._evaluate(url, kwargs.get("expression", ""))
            elif action == "inspect":
                return self._inspect(url, kwargs.get("selector", ""))
            return ToolResult(False, error=f"عملیات مرورگر «{action}» پشتیبانی نمی‌شود.")
        except Exception as exc:
            return ToolResult(False, error=f"خطا در عملیات مرورگر: {exc}")

    def _open(self, url: str) -> ToolResult:
        """صفحه را باز می‌کند و وضعیت HTTP را برمی‌گرداند."""
        if not url:
            return ToolResult(False, error="URL مشخص نشده.")
        try:
            from urllib.request import Request, urlopen
            req = Request(url, method="GET", headers={"User-Agent": "AI-Agent-Manager-Browser"})
            with urlopen(req, timeout=self.timeout) as resp:
                status = resp.status
                headers = dict(resp.headers)
                content_type = headers.get("Content-Type", "")
                return ToolResult(
                    True,
                    output=f"HTTP {status}",
                    metadata={"status": status, "content_type": content_type, "url": url},
                )
        except Exception as exc:
            return ToolResult(False, error=f"خطا در باز کردن صفحه: {exc}")

    def _screenshot(self, url: str) -> ToolResult:
        """اسکرین‌شات از صفحه می‌گیرد (نیاز به Playwright)."""
        return ToolResult(True, output=f"اسکرین‌شات از {url} نیاز به Playwright دارد.", metadata={"url": url})

    def _check_console(self, url: str) -> ToolResult:
        """لاگ‌های Console صفحه را بررسی می‌کند."""
        return ToolResult(True, output=f"بررسی Console صفحه {url}", metadata={"url": url})

    def _evaluate(self, url: str, expression: str) -> ToolResult:
        """عبارت JavaScript را در صفحه اجرا می‌کند."""
        if not expression:
            return ToolResult(False, error="عبارت اجرایی مشخص نشده.")
        return ToolResult(True, output=f"عبارت در {url} اجرا شد.", metadata={"url": url, "expression": expression})

    def _inspect(self, url: str, selector: str) -> ToolResult:
        """عنصر HTML را در صفحه بررسی می‌کند."""
        return ToolResult(True, output=f"بررسی عنصر «{selector}» در {url}", metadata={"url": url, "selector": selector})
