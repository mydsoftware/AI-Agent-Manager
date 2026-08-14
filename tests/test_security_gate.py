from manager.engineering_loop import EngineeringLoop, EngineeringState


def test_security_gate_blocks_before_pr():
    created_pr = []
    result = EngineeringLoop(max_attempts=1).run(
        create_branch=lambda: None,
        apply_change=lambda: None,
        check_ci=lambda: "success",
        repair=lambda *args: None,
        get_diff=lambda: "requests.get(url, verify=False)",
        create_pr=lambda: created_pr.append(True),
    )
    assert result.state == EngineeringState.FAILED
    assert result.review_approved is True
    assert result.security_passed is False
    assert created_pr == []


def test_security_gate_allows_clean_change():
    created_pr = []
    result = EngineeringLoop(max_attempts=1).run(
        create_branch=lambda: None,
        apply_change=lambda: None,
        check_ci=lambda: "success",
        repair=lambda *args: None,
        get_diff=lambda: "def clean():\n    return True",
        create_pr=lambda: created_pr.append(True),
    )
    assert result.state == EngineeringState.DONE
    assert result.review_approved is True
    assert result.security_passed is True
    assert created_pr == [True]
