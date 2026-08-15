from pathlib import Path

from manager.wordpress_factory_pipeline import WordPressFactoryPipeline


def test_pipeline_delivers_only_after_package_validation(tmp_path: Path):
    result = WordPressFactoryPipeline().run(
        "یک سایت وردپرسی اختصاصی برای خدمات ماهواره مرکزی با فرم مشاوره بساز",
        str(tmp_path),
    )
    assert result.passed is True
    assert result.package.passed is True
    assert result.delivery is not None
    assert result.delivery.delivered is True
    assert Path(result.delivery.package_path).exists()
    assert Path(result.delivery.manifest_path).exists()
