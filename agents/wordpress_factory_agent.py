from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class WordPressArtifact:
    path: str
    kind: str
    purpose: str


@dataclass(frozen=True)
class WordPressBuildPlan:
    project_name: str
    theme_name: str
    artifacts: tuple[WordPressArtifact, ...]
    tests: tuple[str, ...]


class WordPressFactoryAgent:
    """درخواست سطح بالا را به برنامه ساخت Theme/Plugin وردپرس تبدیل می‌کند."""

    def plan(self, request: str) -> WordPressBuildPlan:
        text = request.strip()
        slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "custom-wordpress-site"
        theme = f"{slug[:32]}-theme"
        artifacts = (
            WordPressArtifact(f"wp-content/themes/{theme}/style.css", "theme", "مشخصات و استایل قالب"),
            WordPressArtifact(f"wp-content/themes/{theme}/functions.php", "theme", "Bootstrap و قابلیت‌های قالب"),
            WordPressArtifact(f"wp-content/themes/{theme}/front-page.php", "theme", "صفحه اصلی اختصاصی"),
            WordPressArtifact(f"wp-content/themes/{theme}/header.php", "theme", "هدر سایت"),
            WordPressArtifact(f"wp-content/themes/{theme}/footer.php", "theme", "فوتر سایت"),
            WordPressArtifact(f"wp-content/themes/{theme}/README.md", "documentation", "راهنمای نصب و توسعه"),
        )
        if any(word in text.lower() for word in ("فرم", "form", "سفارش", "booking", "quote")):
            artifacts += (WordPressArtifact("wp-content/plugins/site-leads/site-leads.php", "plugin", "مدیریت فرم و Lead"),)
        return WordPressBuildPlan(text, theme, artifacts, (
            "theme activation",
            "front page render",
            "responsive layout",
            "php syntax",
            "plugin activation",
        ))
