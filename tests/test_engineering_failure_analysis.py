from manager.engineering_loop import EngineeringLoop, EngineeringState


def test_failure_is_analyzed_before_repair():
    statuses = iter(["failure", "success"])
    analyses = []

    def repair(plan, analysis):
        analyses.append(analysis)

    result = EngineeringLoop(max_attempts=2).run(
        create_branch=lambda: None,
        apply_change=lambda: None,
        check_ci=lambda: next(statuses),
        get_ci_log=lambda: "FAILED tests/test_discount.py::test_expired - AssertionError",
        repair=repair,
        create_pr=lambda: None,
    )

    assert result.state == EngineeringState.DONE
    assert result.attempts == 2
    assert len(analyses) == 1
    assert analyses[0].category == "test"
    assert "tests/test_discount.py::test_expired" in analyses[0].failing_tests
