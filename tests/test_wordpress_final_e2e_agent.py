from pathlib import Path

from agents.wordpress_final_e2e_agent import WordPressFinalE2EAgent


def test_final_e2e_exposes_all_required_stages(tmp_path: Path):
    result = WordPressFinalE2EAgent().run(
        "یک سایت وردپرسی اختصاصی برای خدمات ماهواره مرکزی با فرم مشاوره بساز",
        str(tmp_path),
    )
    assert result.stages == (
        "requirements", "build", "quality", "package", "smoke", "ui",
        "browser", "delivery", "installer",
    )
    assert result.result.package is not None
    assert result.result.smoke_test is not None
    assert result.result.ui_test is not None
    assert result.result.browser_test is not None
