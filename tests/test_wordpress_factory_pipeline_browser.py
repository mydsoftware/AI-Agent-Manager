from pathlib import Path

from manager.wordpress_factory_pipeline import WordPressFactoryPipeline


def test_pipeline_skips_live_browser_without_url(tmp_path: Path):
    result = WordPressFactoryPipeline().run(
        "یک سایت وردپرسی اختصاصی برای خدمات ماهواره مرکزی با فرم مشاوره بساز",
        str(tmp_path),
    )
    assert result.browser_test.passed is True
    assert result.browser_test.executed is False
    assert result.delivery is not None
    assert result.passed is True
