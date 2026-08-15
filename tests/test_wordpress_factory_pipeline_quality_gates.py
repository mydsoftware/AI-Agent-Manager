from pathlib import Path

from manager.wordpress_factory_pipeline import WordPressFactoryPipeline


def test_pipeline_runs_all_production_gates(tmp_path: Path):
    result = WordPressFactoryPipeline().run(
        "یک سایت وردپرسی اختصاصی برای خدمات ماهواره مرکزی با فرم مشاوره بساز",
        str(tmp_path),
    )
    assert result.security_test.checks or result.security_test.findings
    assert result.performance_test.checks or result.performance_test.findings
    assert result.requirement_compliance.checks or result.requirement_compliance.findings
    assert result.passed is True
    assert result.delivery is not None
    assert result.installer is not None
