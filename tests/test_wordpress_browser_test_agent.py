from agents.wordpress_browser_test_agent import WordPressBrowserTestAgent


def test_browser_agent_reports_unavailable_environment_without_crashing():
    result = WordPressBrowserTestAgent().run("http://127.0.0.1:65535")
    assert isinstance(result.passed, bool)
    assert isinstance(result.findings, tuple)
