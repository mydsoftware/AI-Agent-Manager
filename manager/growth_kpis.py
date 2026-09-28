from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GrowthKPI:
    name: str
    definition: str
    source: str
    unit: str = "count"


DEFAULT_KPIS = (
    GrowthKPI("traffic", "بازدید ورودی قابل اندازه‌گیری", "analytics"),
    GrowthKPI("organic_clicks", "کلیک ارگانیک", "search_console"),
    GrowthKPI("leads", "تعداد لید ثبت‌شده", "crm"),
    GrowthKPI("qualified_leads", "لید واجد شرایط", "crm"),
    GrowthKPI("conversion_rate", "نرخ تبدیل لید به مشتری", "crm", "%"),
    GrowthKPI("customers", "مشتریان جدید", "crm"),
    GrowthKPI("revenue", "درآمد منتسب به قیف", "finance"),
)
