from __future__ import annotations

from dataclasses import dataclass
from typing import Any


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


def calculate_conversion_rate(leads: int, customers: int) -> float:
    """نرخ تبدیل را بدون تقسیم بر صفر محاسبه می‌کند."""
    if leads <= 0:
        return 0.0
    return round((customers / leads) * 100, 4)


def normalize_kpi_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Snapshot خام را به شکل قابل گزارش‌دهی و بدون حدس‌زدن داده تبدیل می‌کند."""
    result: dict[str, Any] = {}
    for kpi in DEFAULT_KPIS:
        value = snapshot.get(kpi.name)
        result[kpi.name] = {
            "value": value,
            "unit": kpi.unit,
            "source": kpi.source,
            "observed": value is not None,
        }

    leads = snapshot.get("leads")
    customers = snapshot.get("customers")
    if isinstance(leads, int) and isinstance(customers, int):
        result["conversion_rate"] = {
            "value": calculate_conversion_rate(leads, customers),
            "unit": "%",
            "source": "derived",
            "observed": True,
        }

    return result
