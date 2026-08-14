from agents.security_agent import SecurityAgent


def test_security_agent_passes_clean_diff():
    result = SecurityAgent().scan("def add(a, b):\n    return a + b\n")
    assert result.passed is True


def test_security_agent_blocks_eval():
    result = SecurityAgent().scan("value = eval(user_input)")
    assert result.passed is False
    assert any(item.category == "code-execution" for item in result.findings)


def test_security_agent_blocks_hardcoded_secret():
    result = SecurityAgent().scan("api_key = 'secret-value'")
    assert result.passed is False
    assert any(item.severity == "critical" for item in result.findings)


def test_security_agent_blocks_critical_dependency():
    result = SecurityAgent().scan("clean", "critical vulnerability found")
    assert result.passed is False
