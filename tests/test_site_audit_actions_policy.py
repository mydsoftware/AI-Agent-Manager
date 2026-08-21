from agents.public_site_scanner import PublicSiteScanner
from agents.site_audit_actions import SiteAuditActionPlanner


def test_action_plan_contains_execution_policy():
    scanner = PublicSiteScanner()
    scanner.record_observation(
        scanner.build_observation(url="https://example.com/bad", status=404)
    )
    scanner.record_observation(
        scanner.build_observation(url="https://example.com/no-canonical", status=200, title="صفحه")
    )

    actions = SiteAuditActionPlanner().plan(scanner.observations)

    http = next(item for item in actions if item.issue == "پاسخ HTTP خطادار")
    canonical = next(item for item in actions if item.issue == "Canonical وجود ندارد")
    assert http.mode == "گزارش شود"
    assert canonical.mode == "قابل اصلاح خودکار"
    assert http.policy_reason
    assert canonical.policy_reason
