from pathlib import Path

from agents.wordpress_factory_agent import WordPressFactoryAgent
from manager.wordpress_build_executor import WordPressBuildExecutor


def test_wordpress_executor_builds_files_and_zip(tmp_path: Path):
    plan = WordPressFactoryAgent().plan("یک سایت وردپرسی برای خدمات ماهواره مرکزی بساز")
    result = WordPressBuildExecutor().execute(plan, str(tmp_path))

    assert Path(result.zip_path).exists()
    assert any(path.endswith("style.css") for path in result.files_created)
    assert any(path.endswith("functions.php") for path in result.files_created)
