from agents.wordpress_requirements_agent import WordPressRequirementsAgent


def test_requirements_extracts_satellite_pages_and_features():
    result = WordPressRequirementsAgent().analyze("یک سایت وردپرسی اختصاصی برای خدمات ماهواره مرکزی با فرم مشاوره بساز")
    slugs = {page.slug for page in result.pages}
    assert {"home", "about", "contact", "packages"}.issubset(slugs)
    assert "service-packages" in result.features
    assert "lead-form" in result.features
    assert "responsive" in result.features
