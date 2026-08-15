from manager.engineering_loop import EngineeringLoop, EngineeringState


def test_successful_cycle_reaches_done():
    events = []

    result = EngineeringLoop().run(
        lambda: events.append("branch"),
        lambda: events.append("change"),
        lambda: "success",
        lambda status: events.append(("repair", status)),
        lambda: events.append("pr"),
    )

    assert result.state is EngineeringState.DONE
    assert result.attempts == 1
    assert events == ["branch", "change", "pr"]


def test_pending_ci_does_not_create_pr():
    events = []
    result = EngineeringLoop().run(
        lambda: events.append("branch"),
        lambda: events.append("change"),
        lambda: "in_progress",
        lambda status: events.append(("repair", status)),
        lambda: events.append("pr"),
    )

    assert result.state is EngineeringState.VERIFY
    assert result.ci_status == "in_progress"
    assert "pr" not in events


def test_failed_ci_repairs_then_retries():
    events = []
    statuses = iter(["failure", "success"])

    result = EngineeringLoop().run(
        lambda: events.append("branch"),
        lambda: events.append("change"),
        lambda: next(statuses),
        lambda status: events.append(("repair", status)),
        lambda: events.append("pr"),
    )

    assert result.state is EngineeringState.DONE
    assert result.attempts == 2
    assert ("repair", "failure") in events
    assert "pr" in events


def test_max_attempts_stops_repair_loop():
    repairs = []
    result = EngineeringLoop(max_attempts=2).run(
        lambda: None,
        lambda: None,
        lambda: "failure",
        lambda status: repairs.append(status),
        lambda: None,
    )

    assert result.state is EngineeringState.FAILED
    assert result.attempts == 2
    assert repairs == ["failure"]
