from __future__ import annotations

from manager.engineering_loop import EngineeringLoop, EngineeringState


def test_engineering_loop_repairs_failure_then_passes():
    calls = []
    statuses = iter(["failure", "success"])

    def create_branch():
        calls.append("branch")

    def apply_change():
        calls.append("change")

    def check_ci():
        calls.append("ci")
        return next(statuses)

    def repair(status):
        calls.append(f"repair:{status}")

    def create_pr():
        calls.append("pr")

    result = EngineeringLoop(max_attempts=3).run(
        create_branch, apply_change, check_ci, repair, create_pr
    )

    assert result.state is EngineeringState.DONE
    assert result.attempts == 2
    assert result.ci_status == "success"
    assert result.error is None
    assert calls == ["branch", "change", "ci", "repair:failure", "ci", "pr"]


def test_engineering_loop_stops_after_max_attempts():
    repaired = []

    def repair(status):
        repaired.append(status)

    result = EngineeringLoop(max_attempts=2).run(
        lambda: None,
        lambda: None,
        lambda: "failure",
        repair,
        lambda: None,
    )

    assert result.state is EngineeringState.FAILED
    assert result.attempts == 2
    assert result.ci_status == "failure"
    assert repaired == ["failure"]
