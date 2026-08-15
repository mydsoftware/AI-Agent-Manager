from pathlib import Path

from manager.wordpress_factory_pipeline import WordPressFactoryPipeline


def test_pipeline_requires_final_package_validation(tmp_path: Path):
    result = WordPressFactoryPipeline().run(
        "یک سایت وردپرسی اختصاصی برای خدمات ماهواره مرکزی با فرم مشاوره بساز",
        str(tmp_path),
    )
    assert result.passed is True
    assert result.package.passed is True
    assert result.package.files
    assert Path(result.build.zip_path).exists()
