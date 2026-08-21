from agents.public_site_scanner import PublicSiteScanner
from agents.site_audit_actions import SiteAuditActionPlanner
from agents.site_audit_html import SiteAuditHtmlRenderer


def test_html_shows_immediate_seo_actions():
    scanner = PublicSiteScanner()
    scanner.record_observation(scanner.build_observation(url="https://example.com/bad", status=404))
    report = scanner.generate_report()
    report = SiteAuditActionPlanner().add_to_report(report, scanner.observations)

    html = SiteAuditHtmlRenderer().render(report)

    assert "اقدامات فوری پیشنهادی" in html
    assert "بحرانی" in html
    assert "https://example.com/bad" in html
    assert "وضعیت HTTP" in html
