from agents.public_site_scanner import PublicSiteScanner
from agents.site_audit_report import SiteAuditReportBuilder


def test_site_audit_report_aggregates_scan_results():
    scanner = PublicSiteScanner()
    scanner.record_observation(
        scanner.build_observation(
            url="https://example.com/a",
            status=200,
            canonical_url="https://example.com/main",
        )
    )
    scanner.record_observation(
        scanner.build_observation(
            url="https://example.com/b",
            status=200,
            canonical_url="https://example.com/main",
        )
    )
    scanner.record_redirect("https://example.com/old", 301, "/new")
    scanner.record_failure("https://example.com/fail", "timeout")

    report = SiteAuditReportBuilder().build(
        scanner.observations,
        scanner.failed,
        scanner.duplicate_groups(),
        scanner.redirect_tracker.observations,
    )

    assert report.pages_scanned == 2
    assert report.pages_failed == 1
    assert report.redirects == 1
    assert report.duplicate_groups == 1
    assert report.duplicate_urls == 2
    assert report.to_dict()["errors"]["https://example.com/fail"] == "timeout"
