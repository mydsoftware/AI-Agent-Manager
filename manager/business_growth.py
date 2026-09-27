from __future__ import annotations

from dataclasses import dataclass

from manager.task import Task


@dataclass(frozen=True)
class BusinessGrowthStage:
    """یک مرحله مستقل از چرخه رشد کسب‌وکار."""

    id: str
    title: str
    agent: str
    capability: str


class BusinessGrowthPipeline:
    """Pipeline استاندارد راه‌اندازی، جذب مشتری و بهینه‌سازی کسب‌وکار."""

    STAGES = (
        BusinessGrowthStage("business-strategy", "تحلیل کسب‌وکار و استراتژی", "business-strategy", "business"),
        BusinessGrowthStage("website-builder", "ساخت وب‌سایت", "website-builder", "web"),
        BusinessGrowthStage("seo", "زیرساخت و استراتژی SEO", "seo", "seo"),
        BusinessGrowthStage("content", "موتور محتوا", "content", "content"),
        BusinessGrowthStage("lead-generation", "تولید و شکار لید", "lead-generation", "lead-generation"),
        BusinessGrowthStage("marketing", "اجرای بازاریابی", "marketing", "marketing"),
        BusinessGrowthStage("sales", "پیگیری و تبدیل فروش", "sales", "sales"),
        BusinessGrowthStage("analytics", "اندازه‌گیری قیف", "analytics", "analytics"),
        BusinessGrowthStage("growth-optimizer", "بهینه‌سازی چرخه بعد", "growth-optimizer", "optimization"),
    )

    def build(self, request: str, target: str | None = None) -> list[Task]:
        context = request
        if target:
            context = f"کسب‌وکار هدف: {target}\nدرخواست: {request}"

        tasks: list[Task] = []
        previous: str | None = None
        for stage in self.STAGES:
            task = Task(
                id=f"growth-{stage.id}",
                title=stage.title,
                description=context,
                agent=stage.agent,
                depends_on=[previous] if previous else [],
                capability=stage.capability,
            )
            tasks.append(task)
            previous = task.id
        return tasks
