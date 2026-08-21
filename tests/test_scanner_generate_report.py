from agents.public_site_scanner import PublicSiteScanner


def test_generate_report_uses_current_scanner_state():
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

    report = scanner.generate_report()

    assert report.pages_scanned == 2
    assert report.pages_failed == 1
    assert report.redirects == 1
    assert report.duplicate_groups == 1
    assert report.duplicate_urls == 2
    assert report.errors["https://example.com/fail"] == "timeout"
