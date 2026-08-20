from manager.policy import authorize


def test_pre_contract_allows_only_audit_without_access():
    decision = authorize(action="website-audit", mode="pre_contract", access=False)
    assert decision.allowed is True


def test_pre_contract_rejects_fix():
    decision = authorize(action="fix", mode="pre_contract", access=False)
    assert decision.allowed is False


def test_pre_contract_rejects_access():
    decision = authorize(action="website-audit", mode="pre_contract", access=True)
    assert decision.allowed is False


def test_post_contract_requires_access():
    decision = authorize(action="fix", mode="post_contract", access=False)
    assert decision.allowed is False


def test_post_contract_allows_fix_with_access():
    decision = authorize(action="fix", mode="post_contract", access=True)
    assert decision.allowed is True


def test_invalid_mode_is_rejected():
    decision = authorize(action="audit", mode="unknown", access=False)
    assert decision.allowed is False
