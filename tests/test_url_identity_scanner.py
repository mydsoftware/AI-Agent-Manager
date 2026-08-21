from agents.public_site_scanner import PublicSiteScanner
from agents.robots_policy import RobotsPolicy


def test_queue_deduplicates_equivalent_url_forms():
    scanner = PublicSiteScanner(robots_policy=RobotsPolicy())
    scanner.enqueue([
        "https://www.example.com/about/",
        "https://example.com/about#team",
        "https://example.com/about",
        "HTTPS://EXAMPLE.COM/about/",
    ])

    assert list(scanner.queue) == ["https://example.com/about"]


def test_discovered_links_are_deduplicated_by_identity():
    scanner = PublicSiteScanner()
    observation = scanner.build_observation(
        url="https://example.com/",
        status=200,
        links=[
            "/about/",
            "https://www.example.com/about#team",
            "/contact",
            "/contact/",
        ],
    )

    assert observation.internal_links == [
        "https://example.com/about",
        "https://example.com/contact",
    ]
