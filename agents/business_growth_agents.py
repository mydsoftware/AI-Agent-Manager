from __future__ import annotations

import json

from manager.task import Task
from .base_agent import BaseAgent


class BusinessGrowthAgent(BaseAgent):
    """پایه ایجنت‌های رشد کسب‌وکار؛ خروجی آن یک دستور ساختاریافته برای مرحله بعد است."""

    phase = "business"

    def run(self, task: Task) -> str:
        return json.dumps(
            {
                "type": "business_growth_result",
                "phase": self.phase,
                "status": "ready",
                "target": "کسب‌وکار هدف",
                "input": task.description,
                "next_action": self.next_action,
            },
            ensure_ascii=False,
        )


class BusinessStrategyAgent(BusinessGrowthAgent):
    name = "business-strategy"
    phase = "strategy"
    next_action = "business_strategy"


class WebsiteBuilderAgent(BusinessGrowthAgent):
    name = "website-builder"
    phase = "website"
    next_action = "build_website"


class SEOAgent(BusinessGrowthAgent):
    name = "seo"
    phase = "seo"
    next_action = "technical_and_content_seo"


class ContentAgent(BusinessGrowthAgent):
    name = "content"
    phase = "content"
    next_action = "content_plan"


class LeadGenerationAgent(BusinessGrowthAgent):
    name = "lead-generation"
    phase = "lead_generation"
    next_action = "find_and_qualify_leads"


class MarketingAgent(BusinessGrowthAgent):
    name = "marketing"
    phase = "marketing"
    next_action = "campaign_execution"


class SalesAgent(BusinessGrowthAgent):
    name = "sales"
    phase = "sales"
    next_action = "lead_followup"


class AnalyticsAgent(BusinessGrowthAgent):
    name = "analytics"
    phase = "analytics"
    next_action = "measure_funnel"


class GrowthOptimizerAgent(BusinessGrowthAgent):
    name = "growth-optimizer"
    phase = "optimization"
    next_action = "optimize_next_cycle"
