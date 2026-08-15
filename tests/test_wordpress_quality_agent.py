from pathlib import Path

from agents.wordpress_quality_agent import WordPressQualityAgent


def test_wordpress_quality_accepts_required_theme(tmp_path: Path):
    for name in ("style.css", "functions.php", "front-page.php", "header.php", "footer.php"):
        (tmp_path / name).write_text("<?php\n", encoding="utf-8") if name.endswith(".php") else (tmp_path / name).write_text("/* Theme Name: Demo */\n", encoding="utf-8")
    result = WordPressQualityAgent().validate(str(tmp_path))
    assert result.passed is True


def test_wordpress_quality_detects_missing_file(tmp_path: Path):
    (tmp_path / "style.css").write_text("/* Theme Name: Demo */", encoding="utf-8")
    result = WordPressQualityAgent().validate(str(tmp_path))
    assert result.passed is False
    assert "missing:functions.php" in result.findings


def test_wordpress_quality_blocks_unsafe_php(tmp_path: Path):
    for name in ("style.css", "front-page.php", "header.php", "footer.php"):
        (tmp_path / name).write_text("<?php eval($x);", encoding="utf-8") if name.endswith(".php") else (tmp_path / name).write_text("/* Theme Name: Demo */", encoding="utf-8")
    (tmp_path / "functions.php").write_text("<?php eval($x);", encoding="utf-8")
    result = WordPressQualityAgent().validate(str(tmp_path))
    assert result.passed is False
