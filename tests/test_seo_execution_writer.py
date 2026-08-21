from agents.public_site_scanner import PublicSiteScanner
from agents.seo_execution_engine import SeoExecutionEngine
from agents.site_writer import DryRunSiteWriter


def test_engine_routes_auto_fix_through_writer_without_real_changes():
    scanner = PublicSiteScanner()
    scanner.record_observation(
        scanner.build_observation(
            url="https://example.com/page",
            status=200,
            title="صفحه",
        )
    )

    result = SeoExecutionEngine(writer=DryRunSiteWriter()).execute(
        scanner.observations,
        apply=True,
    )

    canonical = next(item for item in result if item.issue == "Canonical وجود ندارد")
    assert canonical.mode == "قابل اصلاح خودکار"
    assert canonical.executed is True
    assert canonical.changed is False
    assert "Dry Run" in canonical.message
