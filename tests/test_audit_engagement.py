from manager.audit_engagement import AuditEngagement, AuditPhase


def test_pre_contract_audit_needs_no_access():
    engagement = AuditEngagement("https://germantechsat.com")
    assert engagement.can_audit is True
    assert engagement.can_modify is False
    assert "فقط گزارش" in engagement.remediation_status()


def test_post_contract_requires_access_for_modification():
    engagement = AuditEngagement(
        "https://germantechsat.com",
        phase=AuditPhase.POST_CONTRACT,
        accesses=frozenset({"wordpress"}),
    )
    assert engagement.can_audit is True
    assert engagement.can_modify is True


def test_required_access_is_described_without_secrets():
    engagement = AuditEngagement("https://germantechsat.com")
    assert engagement.required_accesses_for("wordpress") == ("wordpress",)
    assert engagement.required_accesses_for("search_console") == ("google_search_console",)
