from __future__ import annotations

import json

from manager.task import Task
from website_audit.deep_engine import DeepWebsiteAuditEngine
from .base_agent import BaseAgent


class WebsiteAuditAgent(BaseAgent):
    """ایجنت بررسی جامع وب‌سایت و ارائه راهکارهای اصلاح به زبان فارسی."""

    name = "website-audit"

    def run(self, task: Task) -> str:
        """آدرس سایت را استخراج و ممیزی عمیق چندصفحه‌ای را اجرا می‌کند."""
        url = self._extract_url(task.description)
        if not url:
            return json.dumps({
                "وضعیت": "نیازمند اطلاعات",
                "پیام": "لطفاً آدرس کامل سایت را ارسال کنید؛ برای نمونه: https://example.com",
                "دستور بعدی": "پس از دریافت آدرس، ممیزی چندصفحه‌ای، ریسپانسیو، سئو، امنیت، عملکرد و دسترس‌پذیری آغاز می‌شود.",
                "دسترسی‌ها": "اگر تحلیل عمیق‌تر لازم باشد، Manager هر دسترسی را جداگانه و مرحله‌به‌مرحله درخواست می‌کند.",
            }, ensure_ascii=False, indent=2)
        report = DeepWebsiteAuditEngine().audit(url, run_browser=True)
        return json.dumps(report.to_dict(), ensure_ascii=False, indent=2)

    @staticmethod
    def _extract_url(text: str) -> str | None:
        for token in text.replace("\n", " ").split():
            candidate = token.strip("()[]{}<>،؛,.")
            if candidate.startswith(("https://", "http://")):
                return candidate
            if candidate.startswith("www.") and "." in candidate:
                return "https://" + candidate
            if "." in candidate and "/" not in candidate and not candidate.startswith("www.") and candidate.count(".") >= 1:
                return "https://" + candidate
        return None
