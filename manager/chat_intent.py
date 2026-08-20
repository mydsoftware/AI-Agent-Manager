from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class ChatCommand:
    """فرمان استخراج‌شده از پیام کاربر برای اجرای AI Agent Manager."""

    فعال: bool
    متن_کار: str
    url: str | None = None


class ChatIntentParser:
    """فرمان AI Agent Manager را از متن گفتگو تشخیص و URL را استخراج می‌کند."""

    ACTIVATION = re.compile(r"\bai\s+agent\s+manager\b", re.IGNORECASE)
    URL = re.compile(r"https?://[^\s<>]+|(?:www\.)?[a-z0-9][a-z0-9.-]+\.[a-z]{2,}(?:/[^\s<>]*)?", re.IGNORECASE)

    def parse(self, message: str) -> ChatCommand:
        match = self.ACTIVATION.search(message or "")
        if not match:
            return ChatCommand(False, message or "", None)

        text = (message[:match.start()] + message[match.end():]).strip()
        url_match = self.URL.search(text)
        url = url_match.group(0).rstrip(".,؛،") if url_match else None
        if url and not url.lower().startswith(("http://", "https://")):
            url = "https://" + url
        return ChatCommand(True, text, url)


def build_task_from_chat(message: str) -> dict[str, str]:
    """پیام فعال‌شده را به Task قابل ارسال به Router تبدیل می‌کند."""
    command = ChatIntentParser().parse(message)
    if not command.فعال:
        raise ValueError("فرمان «AI Agent Manager» در پیام پیدا نشد.")
    if not command.url:
        raise ValueError("برای اجرای ممیزی سایت، آدرس سایت را وارد کنید.")
    return {
        "agent": "website-audit",
        "title": "ممیزی کامل سایت",
        "description": f"ممیزی کامل سایت {command.url}. گزارش مشکلات، شدت، شواهد و راهکارهای اصلاح را کاملاً فارسی ارائه کن.",
        "url": command.url,
    }
