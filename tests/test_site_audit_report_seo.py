from agents.public_site_scanner import PublicSiteScanner


def test_site_report_contains_page_and_global_seo_health():
    scanner = PublicSiteScanner()
    scanner.record_observation(
        scanner.build_observation(
            url="https://example.com/",
            status=200,
            title="صفحه اصلی",
            meta_description="توضیحات",
            h1_count=1,
        )
    )
    scanner.record_observation(
        scanner.build_observation(
            url="https://example.com/bad",
            status=404,
        )
    )

    report = scanner.generate_report()

    assert report.seo_score < 100
    assert report.seo_status in {"عالی", "خوب", "نیازمند بهبود", "ضعیف"}
    assert report.seo_issues > 0
    assert len(report.seo_items) == 2
    assert report.seo_items[0]["url"] == "https://example.com/"
    assert report.seo_items[1]["score"] < report.seo_items[0]["score"]
