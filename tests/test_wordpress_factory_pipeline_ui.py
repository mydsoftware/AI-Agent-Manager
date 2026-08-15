from pathlib import Path

from manager.wordpress_factory_pipeline import WordPressFactoryPipeline


def test_pipeline_requires_ui_test_before_delivery(tmp_path: Path):
    result = WordPressFactoryPipeline().run(
        "یک سایت وردپرسی اختصاصی برای خدمات ماهواره مرکزی با فرم مشاوره بساز",
        str(tmp_path),
    )
    assert result.package.passed is True
    assert result.smoke_test.passed is True
    assert result.ui_test.passed is True
    assert result.delivery is not None
    assert result.installer is not None
    assert result.passed is True
