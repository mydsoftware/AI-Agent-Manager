from manager.business_growth import BusinessGrowthPipeline
from agents.registry import create_default_registry


def test_business_growth_pipeline_has_ordered_end_to_end_stages():
    tasks = BusinessGrowthPipeline().build(
        "از صفر تا صد رشد را اجرا کن",
        target="کارثبت / karsabt.ir",
    )

    assert [task.agent for task in tasks] == [
        "business-strategy",
        "website-builder",
        "seo",
        "content",
        "lead-generation",
        "marketing",
        "sales",
        "analytics",
        "growth-optimizer",
    ]
    assert tasks[0].depends_on == []
    assert tasks[-1].depends_on == ["growth-analytics"]


def test_business_growth_agents_are_registered():
    names = create_default_registry().names()

    for name in (
        "business-strategy",
        "website-builder",
        "seo",
        "content",
        "lead-generation",
        "marketing",
        "sales",
        "analytics",
        "growth-optimizer",
    ):
        assert name in names
