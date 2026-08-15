from pathlib import Path

from agents.wordpress_requirements_agent import WordPressRequirementsAgent
from agents.wordpress_theme_builder import WordPressThemeBuilder


def test_theme_builder_creates_pages_from_requirements(tmp_path: Path):
    requirements = WordPressRequirementsAgent().analyze(
        "یک سایت وردپرسی برای خدمات ماهواره مرکزی با فرم مشاوره بساز"
    )
    created = WordPressThemeBuilder().build(requirements, str(tmp_path))
    assert any(path.endswith("front-page.php") for path in created)
    assert (tmp_path / "page-about.php").exists()
    assert (tmp_path / "page-contact.php").exists()
    assert (tmp_path / "page-packages.php").exists()
    assert (tmp_path / "style.css").exists()
