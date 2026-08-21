from agents.public_site_scanner import PublicSiteScanner
from agents.website_audit import WebsiteAuditAgent


def test_scanner_observation_becomes_farsi_audit_finding():
    scanner = PublicSiteScanner()
    page = scanner.build_observation(
        url="https://example.com",
        status=200,
        title="",
        meta_description="",
        h1_count=0,
        image_count=2,
        images_without_alt=1,
        load_time_ms=4200,
    )

    report = WebsiteAuditAgent().audit("https://example.com", pages=[page])

    assert report.language == "fa"
    assert report.mode == "pre_contract"
    assert any(f.category == "SEO" for f in report.findings)
    assert any(f.category == "Accessibility" for f in report.findings)
    assert any(f.category == "Performance" for f in report.findings)


def test_scanner_limit_is_respected():
    scanner = PublicSiteScanner()
    urls = [f"https://example.com/{i}" for i in range(20)]
    assert len(scanner.limit_urls(urls)) == scanner.MAX_PAGES
