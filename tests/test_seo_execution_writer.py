from agents.public_site_scanner import PublicSiteScanner
from agents.seo_execution_engine import SeoExecutionEngine
from agents.site_writer import DryRunSiteWriter
from agents.wordpress_connection import (
    WordPressConnectionCheck,
    WordPressConnectionConfig,
    WordPressConnectionTester,
)


def test_engine_routes_auto_fix_through_writer_without_real_changes():
    scanner = PublicSiteScanner()
    scanner.record_observation(
        scanner.build_observation(
            url="https://example.com/page",
            status=200,
            title="صفحه",
        )
    )

    # ایجاد connection مجازی که تست‌ها رو رد کنه
    fake_connection = WordPressConnectionConfig(
        site_url="https://example.com",
        username="admin",
        application_password="test-pass",
        agent_token="test-token",
    )

    class FakeConnectionTester:
        def test(self, config):
            return WordPressConnectionCheck(
                reachable=True,
                authenticated=True,
                writer_endpoint_available=True,
                message="اتصال موفق",
            )

    result = SeoExecutionEngine(
        writer=DryRunSiteWriter(),
        connection_tester=FakeConnectionTester(),
    ).execute(
        scanner.observations,
        apply=True,
        connection=fake_connection,
    )

    canonical = next(item for item in result if item.issue == "Canonical وجود ندارد")
    assert canonical.mode == "قابل اصلاح خودکار"
    assert canonical.executed is True
    assert canonical.changed is False
    assert "Dry Run" in canonical.message
