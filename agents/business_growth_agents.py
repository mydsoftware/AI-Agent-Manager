from __future__ import annotations

import json
import os

from manager.growth_contracts import GrowthArtifact
from manager.llm_gateway import LLMGateway
from manager.model_router import ModelRouter
from manager.task import Task
from .base_agent import BaseAgent


class BusinessGrowthAgent(BaseAgent):
    phase = "business"
    next_action = "continue"

    def __init__(self, llm: LLMGateway | None = None, model_router: ModelRouter | None = None) -> None:
        self.llm = llm or LLMGateway()
        self.model_router = model_router or ModelRouter()

    def _complete(self, task: Task, instruction: str, role: str = "planner") -> dict:
        response = self.llm.complete(
            [
                {"role": "system", "content": (
                    f"تو Agent تخصصی {self.name} هستی. مرحله {self.phase}. "
                    "فقط JSON معتبر بده. اقدامی را که ابزارش را نداری انجام‌شده اعلام نکن."
                )},
                {"role": "user", "content": instruction},
            ],
            self.model_router.resolve(role, capability=role),
            temperature=0.15,
        )
        data = json.loads(response.content.strip())
        if not isinstance(data, dict):
            raise ValueError(f"خروجی {self.name} باید JSON object باشد.")
        return data

    def _result(self, data: dict) -> str:
        data.setdefault("type", "business_growth_result")
        data.setdefault("phase", self.phase)
        data.setdefault("next_action", self.next_action)
        return GrowthArtifact(
            kind=data["type"], phase=data["phase"], status=data.get("status", "ready"), payload=data
        ).dumps()

    def run(self, task: Task) -> str:
        return self._result(self._complete(task, task.description))


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
یک برنامه کامل ساخت سایت برای کارثبت تولید کن.
repository={repository}; branch={branch}
خروجی باید engineering_plan داشته باشد:
{{"repository":"...","base":"main","branch":"...","workflow":"ci.yml",
"changes":[{{"path":"...","content":"FULL FILE","message":"..."}}],
"repair_changes":[],"pr":{{"title":"...","body":"...","draft":true}}}}
سایت فارسی RTL، mobile-first، سریع و قابل ایندکس باشد و صفحه‌های:
خانه، ثبت شرکت، پروانه کسب، مجوز مشاغل خانگی، خدمات اداری، کافی‌نت آنلاین،
شهرها، وبلاگ، تماس و فرم Lead را پوشش دهد.
SEO foundation، metadata، canonical، OpenGraph، sitemap، robots و schema را در صورت مناسب بودن اضافه کن.
Secret تولید نکن.
Context:
{task.description}
"""
        return self._result(self._complete(task, instruction, role="developer"))


class SEOAgent(BusinessGrowthAgent):
    name = "seo"
    phase = "seo"
    next_action = "content"

    def run(self, task: Task) -> str:
        instruction = f"""
برای کارثبت یک برنامه SEO اجرایی بساز.
خروجی JSON شامل:
technical_audit، keyword_clusters، service_pages، local_pages،
internal_link_plan، schema_plan، content_gaps، measurement_plan.
کلمات کلیدی را بر اساس intent دسته‌بندی کن و از ادعای حجم جستجوی تأییدنشده خودداری کن.
اگر داده واقعی Search Console/Analytics در context نیست، آن را مشخص کن.
Context:
{task.description}
"""
        return self._result(self._complete(task, instruction, role="planner"))


class ContentAgent(BusinessGrowthAgent):
    name = "content"
    phase = "content"
    next_action = "lead-generation"

    def run(self, task: Task) -> str:
        instruction = f"""
بر اساس SEO context، Content Engine کارثبت را طراحی کن.
خروجی شامل content_calendar، landing_pages، article_briefs،
faq_targets و internal_links باشد.
محتوا باید فارسی، کاربردی، غیرتکراری و متناسب با intent کاربر باشد.
Context:
{task.description}
"""
        return self._result(self._complete(task, instruction, role="planner"))


class LeadGenerationAgent(BusinessGrowthAgent):
    name = "lead-generation"
    phase = "lead_generation"
    next_action = "marketing"

    def run(self, task: Task) -> str:
        instruction = f"""
برای کارثبت سیستم Lead Generation طراحی کن.
خروجی شامل lead_sources، qualification_rules، lead_schema،
capture_points، follow_up_triggers و priority_rules باشد.
دیوار را به‌عنوان کانال اولیه در نظر بگیر، اما بدون credential یا ادعای دسترسی
به دیوار، فقط workflow و adapter contract تعریف کن.
Context:
{task.description}
"""
        return self._result(self._complete(task, instruction, role="planner"))


class MarketingAgent(BusinessGrowthAgent):
    name = "marketing"
    phase = "marketing"
    next_action = "sales"

    def run(self, task: Task) -> str:
        instruction = f"""
برنامه بازاریابی اجرایی کارثبت را بساز.
خروجی شامل channel_plan، campaign_templates، offer_matrix،
creative_briefs، experiment_plan و attribution_plan باشد.
کانال‌های اولیه: SEO، دیوار، واتساپ و محتوای شبکه اجتماعی.
برای هر اقدام KPI تعریف کن.
Context:
{task.description}
"""
        return self._result(self._complete(task, instruction, role="planner"))


class SalesAgent(BusinessGrowthAgent):
    name = "sales"
    phase = "sales"
    next_action = "analytics"

    def run(self, task: Task) -> str:
        instruction = f"""
Sales Engine کارثبت را طراحی کن.
خروجی شامل pipeline_stages، qualification_questions،
message_templates، follow_up_sequence، lost_reasons و conversion_events باشد.
پیام‌ها را بدون ادعای تضمین نتیجه بنویس.
Context:
{task.description}
"""
        return self._result(self._complete(task, instruction, role="planner"))


class AnalyticsAgent(BusinessGrowthAgent):
    name = "analytics"
    phase = "analytics"
    next_action = "growth-optimizer"

    def run(self, task: Task) -> str:
        instruction = f"""
برای کارثبت Measurement System بساز.
خروجی شامل funnel، events، KPI، dashboards، data_sources،
weekly_report_schema و experiment_metrics باشد.
KPIها حداقل شامل traffic، leads، qualified_leads، conversion_rate،
customers و revenue باشند.
Context:
{task.description}
"""
        return self._result(self._complete(task, instruction, role="planner"))


class GrowthOptimizerAgent(BusinessGrowthAgent):
    name = "growth-optimizer"
    phase = "optimization"
    next_action = "repeat_growth_cycle"

    def run(self, task: Task) -> str:
        instruction = f"""
با توجه به کل context، برنامه چرخه بعدی رشد کارثبت را تولید کن.
خروجی شامل findings، bottlenecks، experiments، prioritized_actions،
success_criteria و next_cycle_tasks باشد.
هیچ ranking یا داده‌ای را بدون evidence واقعی قطعی اعلام نکن.
Context:
{task.description}
"""
        return self._result(self._complete(task, instruction, role="planner"))
