from __future__ import annotations

from manager.llm_gateway import LLMGateway
from manager.model_router import ModelRouter
from manager.task import Task
from .base_agent import BaseAgent


class ResearchAgent(BaseAgent):
    """ایجنت تخصصی تحقیق و جمع‌آوری اطلاعات."""

    name = "research"

    def __init__(self, llm: LLMGateway | None = None, model_router: ModelRouter | None = None) -> None:
        self.llm = llm
        self.model_router = model_router or ModelRouter()

    def run(self, task: Task) -> str:
        """تحقیق را در صورت وجود LLM به مدل محلی می‌سپارد."""
        if self.llm is None:
            return f"وظیفه تحقیق دریافت شد: {task.id}"

        model = self.model_router.resolve("researcher", capability=task.capability)
        response = self.llm.complete(
            [
                {"role": "system", "content": "تو ایجنت تحقیق AI-Agent-Manager هستی. مسئله را ساختاریافته تحلیل کن، فرضیات را جدا کن و نتیجه عملی ارائه بده. اگر دسترسی وب نداری، ادعای جست‌وجوی زنده نکن."},
                {"role": "user", "content": task.description},
            ],
            model,
            temperature=0.2,
        )
        return response.content
