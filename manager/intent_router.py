from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RouteDecision:
    intent: str
    capability: str
    role: str


class IntentRouter:
    """طبقه‌بندی سبک درخواست برای انتخاب Agent و مدل محلی."""

    RULES = {
        "vision": ("vision", "vision", "developer"),
        "code": ("coding", "coder", "developer"),
        "test": ("testing", "coding", "qa"),
        "review": ("review", "coding", "developer"),
        "research": ("research", "general", "research"),
        "plan": ("planning", "general", "developer"),
    }

    KEYWORDS = {
        "vision": ("تصویر", "اسکرین‌شات", "screenshot", "image", "ocr", "عکس"),
        "code": ("کد", "code", "برنامه", "پیاده سازی", "پیاده‌سازی", "bug", "خطا"),
        "test": ("تست", "test", "pytest", "e2e", "smoke"),
        "review": ("review", "بازبینی", "ممیزی", "audit", "بررسی کد"),
        "research": ("تحقیق", "research", "بررسی عمیق", "منابع"),
        "plan": ("معماری", "نقشه", "plan", "طراحی", "راهکار"),
    }

    def classify(self, request: str) -> RouteDecision:
        text = request.lower()
        for key, words in self.KEYWORDS.items():
            if any(word.lower() in text for word in words):
                intent, capability, role = self.RULES[key]
                return RouteDecision(intent, capability, role)
        return RouteDecision("general", "general", "developer")
