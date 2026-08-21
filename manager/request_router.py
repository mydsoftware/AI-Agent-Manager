from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class RoutedRequest:
    """درخواست استانداردشده برای انتخاب Agent."""

    agent: str
    url: str | None
    mode: str
    access: bool
    language: str
    description: str


def route_request(request: str) -> RoutedRequest:
    """عبارت طبیعی کاربر را به یک درخواست استاندارد Agent تبدیل می‌کند."""
    text = request.strip()
    lower = text.lower()
    is_website_audit = any(
        phrase in lower
        for phrase in (
            "ai agent manager",
            "بررسی سایت",
            "سایت رو بررسی",
            "سایت را بررسی",
            "ممیزی سایت",
            "audit website",
            "website audit",
            "مشکلاتشو",
            "مشکلاتش را",
            "مشکلاتش رو",
            "راه‌های اصلاح",
            "راههای اصلاح",
            "راه حل اصلاح",
        )
    )
    if not is_website_audit:
        return RoutedRequest(
            agent="developer",
            url=None,
            mode="standard",
            access=False,
            language="fa",
            description=text,
        )

    url = None
    for token in text.replace("،", " ").split():
        candidate = token.strip("()[]{}<>؛،.!؟\"'")
        if candidate.startswith(("http://", "https://")):
            parsed = urlparse(candidate)
            if parsed.netloc:
                url = candidate
                break
        elif "." in candidate and "/" not in candidate and "@" not in candidate:
            candidate_url = f"https://{candidate}"
            parsed = urlparse(candidate_url)
            if parsed.netloc:
                url = candidate_url
                break

    access = any(
        phrase in text
        for phrase in (
            "دسترسی دادم",
            "دسترسی فعال",
            "خودت اصلاح",
            "خودت اصلاحشون",
            "اصلاحشون کن",
            "اصلاح‌شان کن",
            "اصلاحشان کن",
            "access=true",
            "با دسترسی",
        )
    )
    mode = "post_contract" if access else "pre_contract"

    return RoutedRequest(
        agent="website-audit",
        url=url,
        mode=mode,
        access=access,
        language="fa",
        description=text,
    )
