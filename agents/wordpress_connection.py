from __future__ import annotations

from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import json


@dataclass(frozen=True)
class WordPressConnectionConfig:
    """تنظیمات اتصال WordPress؛ Credentialها فقط برای درخواست فعلی استفاده می‌شوند."""
    site_url: str
    username: str
    application_password: str
    agent_token: str
    timeout: int = 15


@dataclass(frozen=True)
class WordPressConnectionCheck:
    """نتیجه بررسی اتصال و سطح دسترسی Endpoint."""
    reachable: bool
    authenticated: bool
    writer_endpoint_available: bool
    message: str


class WordPressConnectionTester:
    """اتصال را بدون ایجاد تغییر در محتوای WordPress بررسی می‌کند."""

    def test(self, config: WordPressConnectionConfig) -> WordPressConnectionCheck:
        endpoint = config.site_url.rstrip("/") + "/wp-json/ai-agent-manager/v1/seo/canonical"
        request = Request(
            endpoint,
            method="OPTIONS",
            headers={"X-AI-Agent-Token": config.agent_token},
        )
        try:
            with urlopen(request, timeout=config.timeout) as response:
                return WordPressConnectionCheck(
                    reachable=True,
                    authenticated=response.status not in (401, 403),
                    writer_endpoint_available=response.status < 500,
                    message="اتصال و Endpoint با موفقیت بررسی شدند.",
                )
        except HTTPError as exc:
            if exc.code in (401, 403):
                return WordPressConnectionCheck(True, False, True, "سایت در دسترس است اما احراز هویت Agent ناموفق است.")
            if exc.code in (404, 405):
                return WordPressConnectionCheck(True, True, False, "سایت در دسترس است اما Endpoint اختصاصی Agent موجود نیست.")
            return WordPressConnectionCheck(True, False, True, f"WordPress پاسخ HTTP {exc.code} داد.")
        except URLError as exc:
            return WordPressConnectionCheck(False, False, False, f"اتصال به سایت برقرار نشد: {exc.reason}")
        except Exception as exc:
            return WordPressConnectionCheck(False, False, False, f"خطای بررسی اتصال: {exc}")
