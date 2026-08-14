from manager.engineering_loop import EngineeringLoop, EngineeringState


def test_repair_agent_plan_is_passed_to_executor_and_retry_succeeds():
    statuses = iter(["failure", "success"])
    calls = []

    result = EngineeringLoop(max_attempts=2).run(
        create_branch=lambda: None,
        apply_change=lambda: None,
        check_ci=lambda: next(statuses),
        get_ci_log=lambda: "FAILED tests/test_app.py::test_login - AssertionError",
        repair=lambda plan, analysis: calls.append((plan, analysis)),
        create_pr=lambda: None,
    )

    assert result.state == EngineeringState.DONE
    assert result.attempts == 2
    assert len(calls) == 1
    plan, analysis = calls[0]
    assert plan["type"] == "repair_plan"
    assert plan["strategy"] == "inspect_failing_test_and_related_code"
    assert analysis.category == "test"
