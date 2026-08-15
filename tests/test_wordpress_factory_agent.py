from agents.wordpress_factory_agent import WordPressFactoryAgent


def test_wordpress_factory_creates_theme_plan():
    plan = WordPressFactoryAgent().plan("یک سایت وردپرسی برای خدمات ماهواره مرکزی بساز")
    assert plan.theme_name.endswith("-theme")
    assert any(item.path.endswith("style.css") for item in plan.artifacts)
    assert "theme activation" in plan.tests


def test_wordpress_factory_adds_lead_plugin_for_forms():
    plan = WordPressFactoryAgent().plan("ساخت سایت وردپرس با فرم درخواست مشاوره")
    assert any(item.kind == "plugin" for item in plan.artifacts)
