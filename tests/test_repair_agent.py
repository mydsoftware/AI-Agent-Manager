from manager.failure_analyzer import FailureAnalyzer
from agents.repair_agent import RepairAgent


def test_repair_agent_builds_plan_from_failure_analysis():
    analysis = FailureAnalyzer().analyze(
        "FAILED tests/test_discount.py::test_expired - AssertionError: expected 900",
        "failure",
    )
    result = RepairAgent().run(analysis)
    assert result["type"] == "repair_plan"
    assert result["strategy"] == "inspect_failing_test_and_related_code"
    assert result["requires_execution"] is True
    assert "tests/test_discount.py::test_expired" in result["reason"]
