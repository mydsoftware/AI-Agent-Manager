from pathlib import Path

from agents.wordpress_plugin_builder import WordPressPluginBuilder
from agents.wordpress_requirements_agent import WordPressRequirementsAgent


def test_plugin_builder_creates_lead_plugin(tmp_path: Path):
    requirements = WordPressRequirementsAgent().analyze(
        "سایت وردپرسی خدمات ماهواره مرکزی با فرم مشاوره"
    )
    created = WordPressPluginBuilder().build(requirements, str(tmp_path))
    plugin = tmp_path / "ai-manager-leads" / "ai-manager-leads.php"
    assert plugin.exists()
    assert plugin in [Path(item) for item in created]
    assert "add_shortcode" in plugin.read_text(encoding="utf-8")
