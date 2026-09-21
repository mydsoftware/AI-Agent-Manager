from __future__ import annotations

from ai_gateway import AIGateway, AIMessage, AIRequest
from manager.task import Task
from .base_agent import BaseAgent


class ResearchAgent(BaseAgent):
    """ایجنت تخصصی تحقیق و جمع‌آوری اطلاعات."""

    name = "research"

    def run(self, task: Task) -> str:
        """تحقیق را از طریق Gateway مستقل OmniRoute/FreeLLMAPI اجرا می‌کند."""
        gateway = AIGateway()
        response = gateway.complete(AIRequest(messages=[
            AIMessage(role="system", content="تو ایجنت تحقیق فارسی هستی. پاسخ دقیق، مستند و خلاصه ارائه کن."),
            AIMessage(role="user", content=task.description),
        ]))
        return response.content
