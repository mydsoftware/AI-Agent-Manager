from __future__ import annotations

import json
import os

from manager.llm_gateway import LLMGateway
from manager.model_router import ModelRouter
from manager.task import Task
from .base_agent import BaseAgent


class BusinessGrowthAgent(BaseAgent):
    """ایجنت پایه رشد با خروجی ساختاریافته و قابل انتقال به مرحله بعد."""

    phase = "business"
    next_action = "continue"

    def __init__(self, llm: LLMGateway | None = None, model_router: ModelRouter | None = None) -> None:
        self.llm = llm or LLMGateway()
        self.model_router = model_router or ModelRouter()

    def _complete(self, task: Task, instruction: str) -> dict:
        response = self.llm.complete(
            [
                {
                    "role": "system",
                    "content": (
                        f"تو Agent تخصصی {self.name} هستی. مرحله: {self.phase}. "
                        "فقط JSON معتبر تولید کن. اقدامی را که ابزارش را نداری انجام‌شده اعلام نکن."
                    ),
                },
                {"role": "user", "content": instruction},
            ],
            self.model_router.resolve("planner", capability="planner"),
            temperature=0.15,
        )
        try:
            data = json.loads(response.content.strip())
        except json.JSONDecodeError as exc:
            raise ValueError(f"خروجی {self.name} JSON معتبر نیست.") from exc
        if not isinstance(data, dict):
            raise ValueError(f"خروجی {self.name} باید object باشد.")
        return data

    def run(self, task: Task) -> str:
        data = self._complete(task, task.description)
        data.setdefault("type", "business_growth_result")
        data.setdefault("phase", self.phase)
        data.setdefault("next_action", self.next_action)
        return json.dumps(data, ensure_ascii=False)


class BusinessStrategyAgent(BusinessGrowthAgent):
    name = "business-strategy"
    phase = "strategy"
    next_action = "website-builder"


class WebsiteBuilderAgent(BusinessGrowthAgent):
    name = "website-builder"
    phase = "website"
    next_action = "seo"

    def run(self, task: Task) -> str:
        repository = os.getenv("BUSINESS_GROWTH_REPOSITORY", "mydsoftware/karsabt")
        branch = os.getenv("BUSINESS_GROWTH_BRANCH", "feature/website-foundation")
        instruction = f"""
برای کسب‌وکار هدف، یک برنامه واقعی ساخت سایت تولید کن.
Target repository: {repository}
Target branch: {branch}

در خروجی علاوه بر اطلاعات استراتژی، این ساختار را تولید کن:
{{
  "type":"business_growth_result",
  "phase":"website",
  "engineering_plan": {{
    "repository":"{repository}",
    "base":"main",
    "branch":"{branch}",
    "workflow":"ci.yml",
    "changes":[
      {{"path":"relative/path","content":"FULL FILE CONTENT","message":"commit message"}}
    ],
    "repair_changes":[],
    "pr":{{"title":"...","body":"...","draft":true}}
  }}
}}

برای کارثبت:
- فارسی و RTL
- mobile-first
- صفحات خدمات ثبت شرکت، پروانه کسب، مشاغل خانگی، خدمات اداری و کافی‌نت آنلاین
- صفحه اصلی و صفحات خدمت قابل ایندکس
- فرم Lead
- SEO foundation
- sitemap/robots/schema در صورت مناسب بودن
- بدون Secret
- فایل‌ها باید کامل و قابل commit باشند

Context:
{task.description}
"""
        data = self._complete(task, instruction)
        data.setdefault("type", "business_growth_result")
        data["phase"] = "website"
        data["next_action"] = "seo"
        return json.dumps(data, ensure_ascii=False)


class SEOAgent(BusinessGrowthAgent):
    name = "seo"
    phase = "seo"
    next_action = "content"


class ContentAgent(BusinessGrowthAgent):
    name = "content"
    phase = "content"
    next_action = "lead-generation"


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
    next_action = "growth-optimizer"


class GrowthOptimizerAgent(BusinessGrowthAgent):
    name = "growth-optimizer"
    phase = "optimization"
    next_action = "repeat_growth_cycle"
