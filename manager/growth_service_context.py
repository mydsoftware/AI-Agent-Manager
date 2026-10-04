from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class GrowthServiceContext:
    """تنظیمات سرویس‌های رشد؛ مقدار Secret فقط از environment خوانده می‌شود."""

    search_console_property: str | None = None
    analytics_property: str | None = None
    crm_base_url: str | None = None
    crm_api_key: str | None = None
    whatsapp_base_url: str | None = None
    whatsapp_api_key: str | None = None
    lead_source_base_url: str | None = None
    lead_source_api_key: str | None = None

    @classmethod
    def from_env(cls) -> "GrowthServiceContext":
        return cls(
            search_console_property=os.getenv("GROWTH_SEARCH_CONSOLE_PROPERTY"),
            analytics_property=os.getenv("GROWTH_ANALYTICS_PROPERTY"),
            crm_base_url=os.getenv("GROWTH_CRM_BASE_URL"),
            crm_api_key=os.getenv("GROWTH_CRM_API_KEY"),
            whatsapp_base_url=os.getenv("GROWTH_WHATSAPP_BASE_URL"),
            whatsapp_api_key=os.getenv("GROWTH_WHATSAPP_API_KEY"),
            lead_source_base_url=os.getenv("GROWTH_LEAD_SOURCE_BASE_URL"),
            lead_source_api_key=os.getenv("GROWTH_LEAD_SOURCE_API_KEY"),
        )

    def configured(self, service: str) -> bool:
        required = {
            "search_console": (self.search_console_property,),
            "analytics": (self.analytics_property,),
            "crm": (self.crm_base_url, self.crm_api_key),
            "whatsapp": (self.whatsapp_base_url, self.whatsapp_api_key),
            "lead_source": (self.lead_source_base_url, self.lead_source_api_key),
        }
        values = required.get(service)
        if values is None:
            raise ValueError(f"سرویس ناشناخته: {service}")
        return all(bool(value) for value in values)
