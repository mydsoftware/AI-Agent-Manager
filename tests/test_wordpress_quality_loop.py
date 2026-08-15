from pathlib import Path

from manager.wordpress_quality_loop import WordPressQualityLoop


def test_quality_loop_repairs_missing_theme_files(tmp_path: Path):
    (tmp_path / "style.css").write_text("/* Theme Name: Demo */", encoding="utf-8")
    result = WordPressQualityLoop(max_attempts=2).run(str(tmp_path))
    assert result.passed is True
    assert result.attempts == 2
    assert (tmp_path / "functions.php").exists()
    assert (tmp_path / "front-page.php").exists()


def test_quality_loop_stops_on_unrepairable_security_issue(tmp_path: Path):
    for name in ("style.css", "functions.php", "front-page.php", "header.php", "footer.php"):
        if name.endswith(".php"):
            (tmp_path / name).write_text("<?php eval($x);", encoding="utf-8")
        else:
            (tmp_path / name).write_text("/* Theme Name: Demo */", encoding="utf-8")
    result = WordPressQualityLoop(max_attempts=2).run(str(tmp_path))
    assert result.passed is False
