from agents.public_site_scanner import PublicSiteScanner


def test_redirect_is_recorded_and_destination_is_queued():
    scanner = PublicSiteScanner()
    observation = scanner.build_observation(
        url="https://example.com/old-page",
        status=301,
        location="/new-page",
    )

    assert observation.redirect is not None
    assert observation.redirect.status == 301
    assert observation.redirect.source_url == "https://example.com/old-page"
    assert observation.redirect.destination_url == "https://example.com/new-page"
    assert list(scanner.queue) == ["https://example.com/new-page"]
    assert scanner.redirect_tracker.observations == [observation.redirect]


def test_non_redirect_response_has_no_redirect_observation():
    scanner = PublicSiteScanner()
    observation = scanner.build_observation(
        url="https://example.com/about",
        status=200,
        location="/other",
    )

    assert observation.redirect is None
    assert list(scanner.queue) == []
