from __future__ import annotations

from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class WordPressConnectionCheck:
    """نتیجه بررسی فقط‌خواندنی اتصال WordPress."""
    reachable: bool
    endpoint_available: bool
    token_valid: bool | None
    message: str


class WordPressConnectionChecker:
    """اتصال Agent به WordPress را بدون ایجاد هیچ تغییری بررسی می‌کند."""

    def check(self, site_url: str, agent_token: str, timeout: int = 10) -> WordPressConnectionCheck:
        endpoint = site_url.rstrip("/") + "/wp-json/ai-agent-manager/v1/seo/canonical"
        request = Request(endpoint, method="OPTIONS", headers={"X-AI-Agent-Token": agent_token})
        try:
            with urlopen(request, timeout=timeout) as response:
                return WordPressConnectionCheck(True, 200 <= response.status < 500, None, "سایت در دسترس است.")
        except HTTPError as exc:
            if exc.code in (401, 403):
                return WordPressConnectionCheck(True, True, False, "Endpoint در دسترس است اما توکن معتبر نیست یا دسترسی کافی ندارد.")
            if exc.code in (404, 405):
                return WordPressConnectionCheck(True, False, None, "سایت در دسترس است اما Endpoint اختصاصی Agent فعال نیست.")
            return WordPressConnectionCheck(True, True, None, f"سایت پاسخ HTTP {exc.code} داد.")
        except URLError as exc:
            return WordPressConnectionCheck(False, False, None, f"اتصال به سایت برقرار نشد: {exc.reason}")
        except Exception as exc:
            return WordPressConnectionCheck(False, False, None, f"خطای بررسی اتصال: {exc}")
