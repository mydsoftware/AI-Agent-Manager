from agents.public_site_scanner import PageObservation
from agents.seo_health import SeoHealthAnalyzer


def test_healthy_page_gets_high_seo_score():
    page = PageObservation(
        url="https://example.com/",
        status=200,
        title="صفحه اصلی",
        meta_description="توضیحات صفحه",
        h1_count=1,
        image_count=1,
        images_without_alt=0,
    )
    result = SeoHealthAnalyzer().analyze(page)
    assert result.score == 100
    assert result.status == "عالی"
    assert result.issues == ()


def test_page_with_seo_problems_gets_lower_score():
    page = PageObservation(
        url="https://example.com/",
        status=404,
        h1_count=2,
        image_count=3,
        images_without_alt=3,
    )
    result = SeoHealthAnalyzer().analyze(page)
    assert result.score < 50
    assert "پاسخ HTTP خطادار" in result.issues
    assert "عنوان صفحه وجود ندارد" in result.issues
    assert "تصاویر بدون Alt وجود دارد" in result.issues
