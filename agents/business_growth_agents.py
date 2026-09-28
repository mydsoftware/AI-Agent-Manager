from __future__ import annotations

import json
import os

from manager.llm_gateway import LLMGateway
from manager.model_router import ModelRouter
from manager.task import Task
from .base_agent import BaseAgent


class BusinessGrowthAgent(BaseAgent):
    """ایجنت پایه رشد کسب‌وکار با خروجی JSON قابل مصرف توسط مرحله بعد."""

    phase = "business"
    next_action = "continue"

    def __init__(self, llm: LLMGateway | None = None, model_router: ModelRouter | None = None) -> None:
        self.llm = llm or LLMGateway()
        self.model_router = model_router or ModelRouter()

    def _complete(self, task: Task, role: str = "planner") -> str:
        prompt = f"""تو {self.name} در AI-Agent-Manager هستی.
هدف: اجرای مرحله {self.phase} از چرخه رشد کسب‌وکار.
خروجی فقط JSON معتبر باشد و برای Agent مرحله بعد قابل مصرف باشد.
از ادعای انجام اقدام خارجی که ابزارش در اختیار تو نیست خودداری کن.
درخواست و context:
{task.description}
"""
        model = self.model_router.resolve(role, capability=role)
        response = self.llm.complete(
            [
                {"role": "system", "content": prompt},
                {"role": "user", "content": task.description},
            ],
            model,
            temperature=0.15,
        )
        return response.content.strip()

    def run(self, task: Task) -> str:
        try:
            raw = self._complete(task)
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                parsed.setdefault("type", "business_growth_result")
                parsed.setdefault("phase", self.phase)
                parsed.setdefault("next_action", self.next_action)
                return json.dumps(parsed, ensure_ascii=False)
        except Exception as exc:
            return json.dumps(
                {
                    "type": "business_growth_result",
                    "phase": self.phase,
                    "status": "failed",
                    "next_action": self.next_action,
                    "error": str(exc),
                },
                ensure_ascii=False,
            )
        return json.dumps(
            {
                "type": "business_growth_result",
                "phase": self.phase,
                "status": "invalid_model_output",
                "next_action": self.next_action,
            },
            ensure_ascii=False,
        )


class BusinessStrategyAgent(BusinessGrowthAgent):
    name = "business-strategy"
    phase = "strategy"
    next_action = "website_builder"


class WebsiteBuilderAgent(BusinessGrowthAgent):
    name = "website-builder"
    phase = "website"
    next_action = "seo_foundation"

    def run(self, task: Task) -> str:
        prompt = task.description + """
اگر ساخت سایت لازم است، خروجی JSON شامل development_plan هم تولید کن:
{"type":"business_growth_result","phase":"website","development_plan":{"engineering_loop":true,"repository":"owner/repo","branch":"...","changes":[]}}
فایل‌ها باید محتوای کامل داشته باشند و Secret نداشته باشند.
"""
        task.description = prompt
        return super().run(task)


class SEOAgent(BusinessGrowthAgent):
    name = "seo"
    phase = "seo"
    next_action = "content"


class ContentAgent(BusinessGrowthAgent):
    name = "content"
    phase = "content"
    next_action = "lead_generation"


class LeadGenerationAgent(BusinessGrowthAgent):
    name = "lead-generation"
    phase = "lead_generation"
    next_action = "marketing"


class MarketingAgent(BusinessGrowthAgent):
    name = "marketing"
    phase = "marketing"
    next_action = "sales"


class SalesAgent(BusinessGrowthAgent):
    name = "sales"
    phase = "sales"
    next_action = "analytics"


class AnalyticsAgent(BusinessGrowthAgent):
    name = "analytics"
    phase = "analytics"
    next_action = "growth_optimizer"


class GrowthOptimizerAgent(BusinessGrowthAgent):
    name = "growth-optimizer"
    phase = "optimization"
    next_action = "repeat_growth_cycle"
