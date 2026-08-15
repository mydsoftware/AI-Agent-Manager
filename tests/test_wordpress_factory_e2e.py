from pathlib import Path

from manager.wordpress_factory_pipeline import WordPressFactoryPipeline


def test_wordpress_factory_full_e2e(tmp_path: Path):
    result = WordPressFactoryPipeline().run(
        "یک سایت وردپرسی اختصاصی برای خدمات ماهواره مرکزی با فرم مشاوره بساز",
        str(tmp_path),
    )
    assert result.passed is True
    assert result.package.passed is True
    assert result.smoke_test.passed is True
    assert result.ui_test.passed is True
    assert result.browser_test.passed is True
    assert result.delivery is not None and result.delivery.delivered is True
    assert result.installer is not None and result.installer.prepared is True
