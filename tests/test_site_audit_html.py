from agents.public_site_scanner import PublicSiteScanner
from agents.site_audit_html import SiteAuditHtmlRenderer


def test_html_report_is_persian_rtl_and_contains_summary():
    scanner = PublicSiteScanner()
    scanner.record_observation(
        scanner.build_observation(
            url="https://example.com/",
            status=200,
            title="صفحه اصلی",
        )
    )
    report = scanner.generate_report()
    html = SiteAuditHtmlRenderer().render(report)

    assert '<html lang="fa" dir="rtl">' in html
    assert "گزارش ممیزی سایت" in html
    assert "صفحات اسکن‌شده" in html
    assert "https://example.com/" in html
