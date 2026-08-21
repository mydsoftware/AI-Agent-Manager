from agents.public_site_scanner import PublicSiteScanner


def test_self_canonical_is_recorded():
    scanner = PublicSiteScanner()
    observation = scanner.build_observation(
        url="https://example.com/about",
        status=200,
        canonical_url="/about/",
    )

    assert observation.canonical is not None
    assert observation.canonical.is_self_canonical is True
    assert observation.canonical.is_missing is False
    assert observation.canonical.is_external is False


def test_missing_canonical_is_reported():
    scanner = PublicSiteScanner()
    observation = scanner.build_observation(
        url="https://example.com/about",
        status=200,
    )

    assert observation.canonical is not None
    assert observation.canonical.is_missing is True


def test_external_canonical_is_reported():
    scanner = PublicSiteScanner()
    observation = scanner.build_observation(
        url="https://example.com/about",
        status=200,
        canonical_url="https://other.example/about",
    )

    assert observation.canonical is not None
    assert observation.canonical.is_external is True
