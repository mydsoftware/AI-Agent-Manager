from __future__ import annotations

from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class WordPressConnectionConfig:
    """تنظیمات اتصال WordPress بدون ذخیره‌سازی Credential."""
    site_url: str
    username: str
    application_password: str
    agent_token: str
    timeout: int = 15


@dataclass(frozen=True)
class WordPressConnectionCheck:
    """نتیجه بررسی دسترسی WordPress."""
    reachable: bool
    authenticated: bool
    writer_endpoint_available: bool
    message: str


class WordPressConnectionTester:
    """اتصال را بدون اجرای عملیات Write بررسی می‌کند."""

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
                    authenticated=True,
                    writer_endpoint_available=200 <= response.status < 300,
                    message="اتصال WordPress و Endpoint با موفقیت بررسی شد.",
                )
        except HTTPError as exc:
            if exc.code in (401, 403):
                return WordPressConnectionCheck(True, False, True, "احراز هویت Agent ناموفق است.")
            if exc.code in (404, 405):
                return WordPressConnectionCheck(True, True, False, "Endpoint اختصاصی Agent پیدا نشد.")
            return WordPressConnectionCheck(True, False, False, f"WordPress پاسخ HTTP {exc.code} داد.")
        except URLError as exc:
            return WordPressConnectionCheck(False, False, False, f"اتصال به سایت برقرار نشد: {exc.reason}")
        except Exception as exc:
            return WordPressConnectionCheck(False, False, False, f"خطای بررسی اتصال: {exc}")
