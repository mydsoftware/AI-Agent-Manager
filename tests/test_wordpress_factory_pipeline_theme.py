from pathlib import Path

from manager.wordpress_factory_pipeline import WordPressFactoryPipeline


def test_pipeline_places_requirement_pages_in_final_theme(tmp_path: Path):
    result = WordPressFactoryPipeline().run(
        "یک سایت وردپرسی اختصاصی برای خدمات ماهواره مرکزی با فرم مشاوره بساز",
        str(tmp_path),
    )
    assert result.passed is True
    assert (Path(result.build.root) / "front-page.php").exists()
    assert (Path(result.build.root) / "page-about.php").exists()
    assert (Path(result.build.root) / "page-contact.php").exists()
    assert (Path(result.build.root) / "page-packages.php").exists()
    assert Path(result.build.zip_path).exists()
