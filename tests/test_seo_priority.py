from agents.seo_health import SeoHealth
from agents.seo_priority import SeoPriorityAnalyzer


def test_seo_issues_are_prioritized():
    health = SeoHealth(
        score=40,
        status="ضعیف",
        issues=(
            "توضیحات متا وجود ندارد",
            "پاسخ HTTP خطادار",
            "عنوان صفحه وجود ندارد",
            "تصاویر بدون Alt وجود دارد",
        ),
    )

    result = SeoPriorityAnalyzer().analyze(health)

    assert result[0].issue == "پاسخ HTTP خطادار"
    assert result[0].severity == "بحرانی"
    assert result[0].priority == 1
    assert result[1].severity == "زیاد"
    assert result[-1].severity == "کم"
