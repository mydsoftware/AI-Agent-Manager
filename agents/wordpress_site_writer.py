from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import json

from agents.site_writer import SiteWriter, WriterResult


@dataclass(frozen=True)
class WordPressWriterConfig:
    """تنظیمات اتصال Writer به WordPress."""
    site_url: str
    username: str
    application_password: str
    timeout: int = 20


class WordPressSiteWriter(SiteWriter):
    """Writer محدود WordPress برای اعمال Canonical با API استاندارد REST."""

    def __init__(self, config: WordPressWriterConfig) -> None:
        self.config = config

    def set_canonical(self, url: str, canonical_url: str) -> WriterResult:
        """Canonical را فقط از طریق یک Endpoint اختصاصی و امن اعمال می‌کند."""
        endpoint = self.config.site_url.rstrip("/") + "/wp-json/ai-agent-manager/v1/seo/canonical"
        payload: dict[str, Any] = {"url": url, "canonical_url": canonical_url}
        auth = f"{self.config.username}:{self.config.application_password}".encode("utf-8")
        import base64
        request = Request(
            endpoint,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Basic " + base64.b64encode(auth).decode("ascii"),
            },
        )
        try:
            with urlopen(request, timeout=self.config.timeout) as response:
                body = response.read().decode("utf-8", errors="replace")
                return WriterResult(
                    success=200 <= response.status < 300,
                    changed=True,
                    message=f"WordPress Writer پاسخ {response.status} دریافت کرد: {body[:300]}",
                )
        except HTTPError as exc:
            return WriterResult(False, f"WordPress Writer خطای HTTP {exc.code} دریافت کرد.", False)
        except URLError as exc:
            return WriterResult(False, f"اتصال به WordPress برقرار نشد: {exc.reason}", False)
        except Exception as exc:
            return WriterResult(False, f"خطای غیرمنتظره Writer: {exc}", False)
