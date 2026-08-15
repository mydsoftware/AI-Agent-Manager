from pathlib import Path

from manager.wordpress_factory_pipeline import WordPressFactoryPipeline


def test_wordpress_factory_pipeline_builds_and_validates(tmp_path: Path):
    result = WordPressFactoryPipeline().run(
        "یک سایت وردپرسی اختصاصی برای خدمات ماهواره مرکزی بساز",
        str(tmp_path),
    )
    assert result.passed is True
    assert result.quality_attempts == 1
    assert Path(result.build.zip_path).exists()
    assert any(item.path.endswith("style.css") for item in result.plan.artifacts)
