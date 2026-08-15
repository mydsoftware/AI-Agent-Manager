from agents.test_generator_agent import TestGeneratorAgent


def test_generator_creates_core_cases():
    tests = TestGeneratorAgent().generate("افزودن قابلیت ثبت سفارش")
    names = {test.name for test in tests}
    assert "test_happy_path" in names
    assert "test_invalid_input" in names


def test_generator_detects_api_and_security():
    tests = TestGeneratorAgent().generate("add authenticated REST API endpoint")
    categories = {test.category for test in tests}
    assert "api" in categories
    assert "security" in categories


def test_generator_detects_wordpress_project():
    tests = TestGeneratorAgent().generate("build a WordPress custom theme")
    assert any(test.category == "wordpress" for test in tests)
