def test_circular_import_regression_marker():
    from agents.public_site_scanner import PageObservation
    from agents.seo_health import SeoHealthAnalyzer
    from agents.site_audit_report import SiteAuditReport
    from agents.site_audit_actions import SiteAuditActionPlanner
    assert PageObservation is not None
    assert SeoHealthAnalyzer is not None
    assert SiteAuditReport is not None
    assert SiteAuditActionPlanner is not None
