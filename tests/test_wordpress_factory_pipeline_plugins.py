from pathlib import Path
import zipfile

from manager.wordpress_factory_pipeline import WordPressFactoryPipeline


def test_pipeline_builds_plugin_and_packages_it(tmp_path: Path):
    result = WordPressFactoryPipeline().run(
        "یک سایت وردپرسی خدمات ماهواره مرکزی با فرم مشاوره بساز",
        str(tmp_path),
    )
    assert result.passed is True
    assert result.plugins_created
    plugin = Path(result.plugins_created[0])
    assert plugin.exists()
    assert plugin.name == "ai-manager-leads.php"

    with zipfile.ZipFile(result.build.zip_path) as archive:
        names = archive.namelist()
    assert any(name.endswith("wp-content/plugins/ai-manager-leads/ai-manager-leads.php") for name in names)
