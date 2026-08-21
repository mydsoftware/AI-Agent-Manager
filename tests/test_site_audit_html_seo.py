from agents.public_site_scanner import PublicSiteScanner
from agents.site_audit_html import SiteAuditHtmlRenderer


def test_html_contains_global_and_page_seo_scores():
    scanner = PublicSiteScanner()
    scanner.record_observation(
        scanner.build_observation(
            url="https://example.com/",
            status=200,
            title="صفحه اصلی",
            meta_description="توضیحات",
            h1_count=1,
        )
    )
    scanner.record_observation(
        scanner.build_observation(url="https://example.com/bad", status=404)
    )

    html = SiteAuditHtmlRenderer().render(scanner.generate_report())

    assert "امتیاز کلی SEO" in html
    assert "وضعیت SEO" in html
    assert "مشکلات SEO" in html
    assert "امتیاز SEO" in html
    assert "صفحه اصلی" in html
    assert "/100" in html
