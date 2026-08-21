from agents.public_site_scanner import PublicSiteScanner
from agents.site_audit_actions import SiteAuditActionPlanner


def test_action_planner_orders_critical_issues_first():
    scanner = PublicSiteScanner()
    scanner.record_observation(
        scanner.build_observation(url="https://example.com/bad", status=404)
    )
    scanner.record_observation(
        scanner.build_observation(
            url="https://example.com/ok",
            status=200,
            title="صفحه",
            meta_description="توضیح",
            h1_count=1,
        )
    )

    actions = SiteAuditActionPlanner().plan(scanner.observations)

    assert actions
    assert actions[0].priority == 1
    assert actions[0].severity == "بحرانی"
    assert actions[0].url == "https://example.com/bad"
    assert actions[0].action
