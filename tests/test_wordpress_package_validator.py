from pathlib import Path
import zipfile

from agents.wordpress_package_validator import WordPressPackageValidator


def make_zip(path: Path, files: dict[str, str]) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        for name, content in files.items():
            archive.writestr(name, content)


def test_package_validator_accepts_valid_wordpress_zip(tmp_path: Path):
    zip_path = tmp_path / "site.zip"
    make_zip(zip_path, {
        "demo/style.css": "/* Theme Name: Demo */",
        "demo/functions.php": "<?php if (!defined('ABSPATH')) exit;",
    })
    result = WordPressPackageValidator().validate(str(zip_path))
    assert result.passed is True


def test_package_validator_blocks_unsafe_php(tmp_path: Path):
    zip_path = tmp_path / "site.zip"
    make_zip(zip_path, {
        "demo/style.css": "/* Theme Name: Demo */",
        "demo/functions.php": "<?php eval($x);",
    })
    result = WordPressPackageValidator().validate(str(zip_path))
    assert result.passed is False
    assert any(item.startswith("unsafe-code:") for item in result.findings)
