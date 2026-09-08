from __future__ import annotations

from dataclasses import dataclass
from requests import RequestException

from services.url_security import request_public_http


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
        """اتصال را با درخواست OPTIONS امن و DNS-pinned بررسی می‌کند."""
        endpoint = config.site_url.rstrip("/") + "/wp-json/ai-agent-manager/v1/seo/canonical"
        try:
            response = request_public_http(
                endpoint,
                method="OPTIONS",
                headers={"X-AI-Agent-Token": config.agent_token},
                sensitive_headers={"X-AI-Agent-Token"},
                timeout=config.timeout,
            )
            if response.status_code in (401, 403):
                return WordPressConnectionCheck(True, False, True, "سایت در دسترس است اما احراز هویت Agent ناموفق است.")
            if response.status_code in (404, 405):
                return WordPressConnectionCheck(True, True, False, "سایت در دسترس است اما Endpoint اختصاصی Agent موجود نیست.")
            return WordPressConnectionCheck(
                True,
                response.status_code < 400,
                response.status_code < 500,
                "اتصال و Endpoint با موفقیت بررسی شدند." if response.status_code < 500 else f"WordPress پاسخ HTTP {response.status_code} داد.",
            )
        except ValueError as exc:
            return WordPressConnectionCheck(False, False, False, str(exc))
        except RequestException as exc:
            return WordPressConnectionCheck(False, False, False, f"اتصال به سایت برقرار نشد: {exc}")
        except Exception as exc:
            return WordPressConnectionCheck(False, False, False, f"خطای بررسی اتصال: {exc}")
