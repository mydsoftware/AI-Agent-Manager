from agents.public_site_scanner import PublicSiteScanner
from agents.site_audit_actions import SiteAuditActionPlanner
from agents.site_audit_html import SiteAuditHtmlRenderer


def test_html_shows_execution_mode_and_policy_reason():
    scanner = PublicSiteScanner()
    scanner.record_observation(scanner.build_observation(url="https://example.com/bad", status=404))
    report = SiteAuditActionPlanner().add_to_report(scanner.generate_report(), scanner.observations)

    html = SiteAuditHtmlRenderer().render(report)

    assert "روش اجرا" in html
    assert "دلیل تصمیم Agent" in html
    assert "گزارش شود" in html
    assert "اثر مستقیم" in html
