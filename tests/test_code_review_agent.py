from agents.code_review_agent import CodeReviewAgent


def test_code_review_approves_clean_change():
    result = CodeReviewAgent().review("def add(a, b):\n    return a + b\n", tests_passed=True)
    assert result.approved is True
    assert result.findings == ()


def test_code_review_rejects_unsafe_code():
    result = CodeReviewAgent().review("result = eval(user_input)", tests_passed=True)
    assert result.approved is False
    assert any(item.category == "security" for item in result.findings)


def test_code_review_rejects_failed_tests():
    result = CodeReviewAgent().review("clean change", tests_passed=False)
    assert result.approved is False
