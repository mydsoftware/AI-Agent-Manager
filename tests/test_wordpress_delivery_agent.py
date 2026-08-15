from pathlib import Path
import zipfile

from agents.wordpress_delivery_agent import WordPressDeliveryAgent
from agents.wordpress_package_validator import WordPressPackageValidator


def test_delivery_agent_creates_package_and_manifest(tmp_path: Path):
    package = tmp_path / "demo.zip"
    with zipfile.ZipFile(package, "w") as archive:
        archive.writestr("demo/style.css", "/* Theme Name: Demo */")
        archive.writestr("demo/functions.php", "<?php if (!defined('ABSPATH')) exit;")

    validation = WordPressPackageValidator().validate(str(package))
    result = WordPressDeliveryAgent().deliver(str(package), validation, "Demo Site", str(tmp_path / "delivery"))

    assert result.delivered is True
    assert Path(result.package_path).exists()
    assert Path(result.manifest_path).exists()
    assert result.manifest["validation"] == "PASS"
