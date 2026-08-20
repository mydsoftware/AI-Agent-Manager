from __future__ import annotations

from website_audit.remediation import WebsiteRemediationManager


def test_remediation_reaudits_and_keeps_improvement():
    stored = []
    calls = []
    after = WebsiteRemediationManager.snapshot("after", "https://example.com", 90, ["ok"])
    manager = WebsiteRemediationManager(lambda url: after, stored.append)
    before = WebsiteRemediationManager.snapshot("before", "https://example.com", 70, ["seo-1", "ux-1"])

    result = manager.remediate(before, lambda: calls.append("apply"))

    assert calls == ["apply"]
    assert result.status == "موفق"
    assert result.improved is True
    assert result.after == after
    assert len(stored) == 2


def test_remediation_rolls_back_when_score_gets_worse():
    stored = []
    rolled_back = []
    after = WebsiteRemediationManager.snapshot("after", "https://example.com", 50, ["a", "b", "c"])
    manager = WebsiteRemediationManager(lambda url: after, stored.append)
    before = WebsiteRemediationManager.snapshot("before", "https://example.com", 70, ["a"])

    result = manager.remediate(before, lambda: None, rollback=lambda: rolled_back.append(True))

    assert result.status == "بازگشت"
    assert result.improved is False
    assert rolled_back == [True]
    assert len(stored) == 2


def test_remediation_does_not_change_site_when_apply_fails():
    stored = []
    manager = WebsiteRemediationManager(lambda url: None, stored.append)
    before = WebsiteRemediationManager.snapshot("before", "https://example.com", 70, ["a"])

    result = manager.remediate(before, lambda: (_ for _ in ()).throw(RuntimeError("خطای آزمایشی")))

    assert result.status == "ناموفق"
    assert result.after is None
    assert stored == [before]
