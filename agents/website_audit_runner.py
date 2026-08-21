from __future__ import annotations

import json
import re
from urllib.parse import urlparse

from manager.task import Task
from website_audit.pipeline import WebsiteAuditPipeline

from .base_agent import BaseAgent


class WebsiteAuditRunnerAgent(BaseAgent):
    """ایجنت ممیزی سایت: اسکن عمومی، دو فایل فارسی مشکلات/راه‌حل، اصلاح مشروط به دسترسی."""

    name = "website-audit"

    def __init__(self, pipeline: WebsiteAuditPipeline | None = None) -> None:
        self.pipeline = pipeline or WebsiteAuditPipeline()

    def run(self, task: Task) -> str:
        """وظیفه ممیزی را اجرا و مسیر فایل‌های فارسی را برمی‌گرداند."""
        params = _parse_task(task.description)
        result = self.pipeline.run(
            params["url"],
            mode=params["mode"],
            access=params["access"],
            language=params.get("language", "fa"),
            max_pages=params.get("max_pages"),
        )
        return json.dumps(result.to_dict(), ensure_ascii=False)


def _parse_task(description: str) -> dict:
    """پارامترهای URL، mode و access را از متن وظیفه استخراج می‌کند."""
    text = description.strip()
    lower = text.lower()
    mode = "post_contract" if "post_contract" in lower or "بعد از قرارداد" in text else "pre_contract"
    if "حالت: post_contract" in lower or "حالت:post_contract" in lower:
        mode = "post_contract"
    if "حالت: pre_contract" in lower:
        mode = "pre_contract"

    access = False
    if re.search(r"دسترسی:\s*دارد", text) or "access=true" in lower or "access: true" in lower:
        access = True
    if any(phrase in text for phrase in ("دسترسی دادم", "دسترسی فعال", "خودت اصلاح کن", "اصلاحشون کن")):
        access = True
        mode = "post_contract"

    url = None
    for token in text.replace("،", " ").split():
        candidate = token.strip("()[]{}<>؛،.!؟\"'")
        if candidate.startswith(("http://", "https://")):
            parsed = urlparse(candidate)
            if parsed.netloc:
                url = candidate
                break
        elif "." in candidate and " " not in candidate and "@" not in candidate and len(candidate) > 3:
            if re.match(r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", candidate):
                url = f"https://{candidate}"
                break

    url_match = re.search(r"URL:\s*(\S+)", text, re.I)
    if url_match:
        url = url_match.group(1).strip()

    if not url:
        raise ValueError("URL سایت برای ممیزی مشخص نشده است.")

    return {"url": url, "mode": mode, "access": access, "language": "fa", "max_pages": None}
