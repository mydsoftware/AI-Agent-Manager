from agents.public_site_scanner import PublicSiteScanner
from agents.seo_execution_engine import SeoExecutionEngine
from agents.site_writer import DryRunSiteWriter
from agents.wordpress_connection import WordPressConnectionCheck, WordPressConnectionConfig


class FailedConnectionTester:
    def test(self, config):
        return WordPressConnectionCheck(False, False, False, "اتصال آزمایشی ناموفق است.")


def test_write_stops_when_connection_check_fails():
    scanner = PublicSiteScanner()
    scanner.record_observation(scanner.build_observation(
        url="https://example.com/page", status=200, title="صفحه"
    ))

    result = SeoExecutionEngine(
        writer=DryRunSiteWriter(),
        connection_tester=FailedConnectionTester(),
    ).execute(
        scanner.observations,
        apply=True,
        connection=WordPressConnectionConfig("https://example.com", "admin", "pass", "token"),
    )

    assert result
    assert all(item.executed is False for item in result)
    assert all("اجرای Action متوقف شد" in item.message for item in result)
