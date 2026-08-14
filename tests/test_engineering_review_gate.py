from manager.engineering_loop import EngineeringLoop, EngineeringState


def test_pr_is_created_only_after_review_approval():
    created = []
    result = EngineeringLoop(max_attempts=1).run(
        create_branch=lambda: None,
        apply_change=lambda: None,
        check_ci=lambda: "success",
        repair=lambda *_: None,
        create_pr=lambda: created.append(True),
        get_diff=lambda: "def add(a, b):\n    return a + b\n",
    )
    assert result.state == EngineeringState.DONE
    assert result.review_approved is True
    assert created == [True]


def test_pr_is_blocked_when_review_rejects():
    created = []
    result = EngineeringLoop(max_attempts=1).run(
        create_branch=lambda: None,
        apply_change=lambda: None,
        check_ci=lambda: "success",
        repair=lambda *_: None,
        create_pr=lambda: created.append(True),
        get_diff=lambda: "result = eval(user_input)",
    )
    assert result.state == EngineeringState.FAILED
    assert result.review_approved is False
    assert created == []
