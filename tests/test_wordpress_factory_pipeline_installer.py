from pathlib import Path

from manager.wordpress_factory_pipeline import WordPressFactoryPipeline


def test_pipeline_prepares_installer_after_delivery(tmp_path: Path):
    result = WordPressFactoryPipeline().run(
        "یک سایت وردپرسی اختصاصی برای خدمات ماهواره مرکزی با فرم مشاوره بساز",
        str(tmp_path),
    )
    assert result.passed is True
    assert result.delivery is not None
    assert result.installer is not None
    assert result.installer.prepared is True
    assert Path(result.installer.install_script_path).exists()
    assert Path(result.installer.instructions_path).exists()
