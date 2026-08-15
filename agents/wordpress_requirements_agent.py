from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class WordPressPage:
    slug: str
    title: str
    sections: tuple[str, ...]


@dataclass(frozen=True)
class WordPressRequirements:
    site_title: str
    pages: tuple[WordPressPage, ...]
    features: tuple[str, ...]


class WordPressRequirementsAgent:
    """درخواست طبیعی را به صفحات، بخش‌ها و قابلیت‌های قابل ساخت تبدیل می‌کند."""

    def analyze(self, request: str) -> WordPressRequirements:
        text = request.strip()
        pages = [
            WordPressPage("home", "صفحه اصلی", ("hero", "services", "trust", "cta")),
            WordPressPage("about", "درباره ما", ("intro", "company-info", "cta")),
            WordPressPage("contact", "تماس با ما", ("contact-info", "form", "map")),
        ]
        features: list[str] = ["responsive", "navigation", "seo-ready"]
        lower = text.lower()
        if re.search(r"خدمات|service", lower):
            features.append("services-catalog")
        if re.search(r"فرم|مشاوره|درخواست|form|quote", lower):
            features.append("lead-form")
        if re.search(r"ماهواره|satellite", lower):
            pages.append(WordPressPage("packages", "پکیج‌ها و خدمات", ("packages", "comparison", "cta")))
            features.extend(["service-packages", "technical-content"])
        return WordPressRequirements(text, tuple(pages), tuple(dict.fromkeys(features)))
