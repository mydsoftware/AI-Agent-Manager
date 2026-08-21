from agents.public_site_scanner import PublicSiteScanner


def test_scanner_exposes_duplicate_groups_after_observations():
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

    groups = scanner.duplicate_groups()

    assert len(groups) == 1
    assert groups[0].urls == (
        "https://example.com/a",
        "https://example.com/b",
    )
    assert groups[0].canonical_url == "https://example.com/main"
