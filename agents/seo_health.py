from __future__ import annotations

from dataclasses import dataclass

from agents.public_site_scanner import PageObservation


@dataclass(frozen=True)
class SeoHealth:
    """امتیاز سلامت SEO یک صفحه."""
    score: int
    status: str
    issues: tuple[str, ...]


class SeoHealthAnalyzer:
    """محاسبه امتیاز ساده و قابل توضیح SEO بر اساس داده‌های Crawl."""

    def analyze(self, page: PageObservation) -> SeoHealth:
        score = 100
        issues: list[str] = []
        if page.status >= 400:
            score -= 40
            issues.append("پاسخ HTTP خطادار")
        if not page.title.strip():
            score -= 15
            issues.append("عنوان صفحه وجود ندارد")
        if not page.meta_description.strip():
            score -= 10
            issues.append("توضیحات متا وجود ندارد")
        if page.h1_count == 0:
            score -= 10
            issues.append("H1 وجود ندارد")
        elif page.h1_count > 1:
            score -= 5
            issues.append("بیش از یک H1 وجود دارد")
        if page.images_without_alt:
            score -= min(15, page.images_without_alt * 3)
            issues.append("تصاویر بدون Alt وجود دارد")
        if page.canonical and page.canonical.is_missing:
            score -= 5
            issues.append("Canonical وجود ندارد")
        if page.canonical and page.canonical.is_external:
            score -= 5
            issues.append("Canonical به دامنه خارجی اشاره می‌کند")
        score = max(0, min(100, score))
        status = "عالی" if score >= 90 else "خوب" if score >= 75 else "نیازمند بهبود" if score >= 50 else "ضعیف"
        return SeoHealth(score, status, tuple(issues))
