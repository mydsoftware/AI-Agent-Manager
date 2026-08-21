from agents.public_site_scanner import PublicSiteScanner
from agents.seo_execution_engine import SeoExecutionEngine


def test_execution_engine_is_dry_run_by_default():
    scanner = PublicSiteScanner()
    scanner.record_observation(scanner.build_observation(url="https://example.com/bad", status=404))

    result = SeoExecutionEngine().execute(scanner.observations)

    assert result
    assert all(item.executed is False for item in result)
    assert all("هیچ تغییری" in item.message or "Writer" in item.message for item in result)


def test_apply_flag_does_not_write_without_safe_writer():
    scanner = PublicSiteScanner()
    scanner.record_observation(scanner.build_observation(url="https://example.com/page", status=200, title="صفحه"))

    result = SeoExecutionEngine().execute(scanner.observations, apply=True)

    assert all(item.executed is False for item in result)
    assert all("Writer امن" in item.message for item in result)
