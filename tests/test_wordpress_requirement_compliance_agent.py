from pathlib import Path
import zipfile

from agents.wordpress_requirement_compliance_agent import WordPressRequirementComplianceAgent


def test_requirement_compliance_accepts_requested_satellite_site(tmp_path: Path):
    package = tmp_path / "site.zip"
    with zipfile.ZipFile(package, "w") as archive:
        archive.writestr("demo/satellite-services.php", "<?php // satellite services ماهواره")
        archive.writestr("demo/contact-form.php", "<?php // consultation form")
    result = WordPressRequirementComplianceAgent().run(
        "یک سایت وردپرسی برای خدمات ماهواره با فرم مشاوره بساز", str(package)
    )
    assert result.passed is True
    assert "requirement:satellite" in result.checks
    assert "requirement:contact-form" in result.checks


def test_requirement_compliance_detects_missing_feature(tmp_path: Path):
    package = tmp_path / "site.zip"
    with zipfile.ZipFile(package, "w") as archive:
        archive.writestr("demo/index.php", "<?php echo 'hello';")
    result = WordPressRequirementComplianceAgent().run(
        "یک سایت فروشگاهی با ووکامرس بساز", str(package)
    )
    assert result.passed is False
    assert "missing:requirement:woocommerce" in result.findings
