from manager.failure_analyzer import FailureAnalyzer


def test_failure_analyzer_detects_failed_pytest():
    log = "FAILED tests/test_discount.py::test_expired_code - AssertionError: expected 900"
    result = FailureAnalyzer().analyze(log, "failure")
    assert result.category == "test"
    assert "tests/test_discount.py::test_expired_code" in result.failing_tests
    assert "AssertionError" not in result.root_cause_hint


def test_failure_analyzer_detects_import_failure():
    log = "ModuleNotFoundError: No module named 'payments'"
    result = FailureAnalyzer().analyze(log, "failure")
    assert result.category == "dependency"


def test_failure_analyzer_success():
    result = FailureAnalyzer().analyze("43 passed", "success")
    assert result.category == "none"
