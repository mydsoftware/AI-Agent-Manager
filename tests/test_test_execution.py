from manager.test_execution import TestExecutionManager


def test_generated_suite_is_executable():
    manager = TestExecutionManager()
    suite = manager.build_suite("build authenticated REST API", test_command="pytest -q")
    assert len(suite.tests) >= 3
    assert suite.test_command == "pytest -q"

    executed = []
    result = manager.execute(suite, lambda command: executed.append(command) or "PASS")
    assert result == "PASS"
    assert executed == ["pytest -q"]


def test_suite_summary_contains_generated_tests():
    suite = TestExecutionManager().build_suite("build WordPress custom theme")
    summary = TestExecutionManager.summary(suite)
    assert summary["count"] == len(suite.tests)
    assert any(item["category"] == "wordpress" for item in summary["tests"])
